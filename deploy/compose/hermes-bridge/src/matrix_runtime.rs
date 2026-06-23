use std::{fs, path::Path, sync::Arc};

use anyhow::{Context, Result};
use matrix_sdk::{
    authentication::matrix::MatrixSession,
    config::SyncSettings,
    ruma::{
        events::room::{
            member::StrippedRoomMemberEvent,
            message::{MessageType, OriginalSyncRoomMessageEvent, RoomMessageEventContent},
        },
        OwnedUserId,
    },
    Client, Room, RoomState,
};
use serde::{Deserialize, Serialize};
use tokio::sync::Mutex;
use tracing::{error, info, warn};

use crate::{
    audit::{AuditEvent, AuditLogger},
    commands::{command_response, parse_command},
    config::BridgeConfig,
    ollama::OllamaClient,
    policy::{decide_response, MessageContext, ResponseDecision, RoomKind},
};

#[derive(Clone)]
pub struct BridgeState {
    config: Arc<BridgeConfig>,
    audit: AuditLogger,
    ollama: OllamaClient,
    paused: Arc<Mutex<bool>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PersistedSession {
    homeserver_url: String,
    matrix_user_id: OwnedUserId,
    user_session: MatrixSession,
}

pub async fn run(config: BridgeConfig) -> Result<()> {
    let audit = AuditLogger::new(config.audit_log_path.clone());
    let ollama = OllamaClient::new(config.ollama_base_url.clone(), config.local_model.clone());
    let client = restore_or_login(&config).await?;
    let state = BridgeState {
        config: Arc::new(config),
        audit,
        ollama,
        paused: Arc::new(Mutex::new(false)),
    };

    let message_state = state.clone();
    client.add_event_handler(move |event, room| {
        let state = message_state.clone();
        async move {
            if let Err(error) = on_room_message(event, room, state).await {
                error!("room message handler failed: {error:?}");
            }
        }
    });

    let invite_state = state.clone();
    client.add_event_handler(move |event, client, room| {
        let state = invite_state.clone();
        async move {
            if let Err(error) = on_invite(event, client, room, state).await {
                error!("invite handler failed: {error:?}");
            }
        }
    });

    let response = client.sync_once(SyncSettings::default()).await?;
    client
        .sync(SyncSettings::default().token(response.next_batch))
        .await?;
    Ok(())
}

async fn restore_or_login(config: &BridgeConfig) -> Result<Client> {
    fs::create_dir_all(&config.store_path).context("create Matrix bridge store directory")?;
    let db_path = config.store_path.join("matrix-sdk-sqlite");
    let session_path = config.store_path.join("session.json");
    let store_passphrase_path = config.store_path.join("store.passphrase");
    let store_passphrase = read_or_create_store_passphrase(&store_passphrase_path)?;

    let client = Client::builder()
        .homeserver_url(config.homeserver_url.as_str())
        .sqlite_store(&db_path, Some(&store_passphrase))
        .build()
        .await
        .context("build Matrix client")?;

    if session_path.exists() {
        let serialized =
            fs::read_to_string(&session_path).context("read persisted Matrix session")?;
        let session: PersistedSession =
            serde_json::from_str(&serialized).context("parse persisted Matrix session")?;
        if session.homeserver_url != config.homeserver_url.as_str()
            || session.matrix_user_id != config.matrix_user_id
        {
            anyhow::bail!("persisted Matrix session does not match configured homeserver/user");
        }
        client
            .restore_session(session.user_session)
            .await
            .context("restore Matrix session")?;
        info!("restored Matrix session for {}", config.matrix_user_id);
        return Ok(client);
    }

    client
        .matrix_auth()
        .login_username(
            config.matrix_user_id.as_str(),
            config.matrix_password.expose_for_login(),
        )
        .initial_device_display_name(&config.device_name)
        .await
        .context("login Matrix bridge user")?;
    let user_session = client
        .matrix_auth()
        .session()
        .context("missing Matrix session after login")?;
    let persisted = PersistedSession {
        homeserver_url: config.homeserver_url.to_string(),
        matrix_user_id: config.matrix_user_id.clone(),
        user_session,
    };
    fs::write(&session_path, serde_json::to_string_pretty(&persisted)?)
        .context("write persisted Matrix session")?;
    info!(
        "logged in and persisted Matrix session for {}",
        config.matrix_user_id
    );
    Ok(client)
}

fn read_or_create_store_passphrase(path: &Path) -> Result<String> {
    if path.exists() {
        return Ok(fs::read_to_string(path)?.trim().to_string());
    }
    let passphrase = format!(
        "{}:{}",
        std::process::id(),
        chrono::Utc::now().timestamp_nanos_opt().unwrap_or_default()
    );
    fs::write(path, &passphrase)?;
    Ok(passphrase)
}

async fn on_invite(
    event: StrippedRoomMemberEvent,
    client: Client,
    room: Room,
    state: BridgeState,
) -> Result<()> {
    let Some(own_user_id) = client.user_id() else {
        return Ok(());
    };
    if event.state_key != own_user_id {
        return Ok(());
    }

    let inviter = event.sender.clone();
    if !state
        .config
        .trusted_inviter_ids
        .iter()
        .any(|trusted| trusted == &inviter)
    {
        state.audit.write(AuditEvent {
            event_type: "invite_denied".to_string(),
            room_id: room.room_id().to_string(),
            actor_id: inviter.to_string(),
            operation_id: "invite".to_string(),
            route: "matrix".to_string(),
            result: "untrusted_inviter".to_string(),
        })?;
        warn!("denied Matrix invite from untrusted inviter");
        return Ok(());
    }

    room.join().await.context("join trusted Matrix invite")?;
    state.audit.write(AuditEvent {
        event_type: "invite_accepted".to_string(),
        room_id: room.room_id().to_string(),
        actor_id: inviter.to_string(),
        operation_id: "invite".to_string(),
        route: "matrix".to_string(),
        result: "trusted_inviter".to_string(),
    })?;
    Ok(())
}

async fn on_room_message(
    event: OriginalSyncRoomMessageEvent,
    room: Room,
    state: BridgeState,
) -> Result<()> {
    if room.state() != RoomState::Joined || event.sender == state.config.matrix_user_id {
        return Ok(());
    }

    let MessageType::Text(text_content) = event.content.msgtype else {
        return Ok(());
    };
    let body = text_content.body;
    let encrypted = format!("{:?}", room.encryption_state()) == "Encrypted";
    let room_kind = if room.is_dm() || room.joined_members_count() <= 2 {
        RoomKind::Direct
    } else {
        RoomKind::Group
    };
    let command = parse_command(&body);
    let mentions_hermes = body
        .to_ascii_lowercase()
        .contains(&state.config.matrix_user_id.localpart().to_ascii_lowercase());
    let paused = *state.paused.lock().await;
    let decision = decide_response(MessageContext {
        encrypted,
        paused,
        mentions_hermes,
        command,
        room_kind,
    });

    match decision {
        ResponseDecision::DenyUnencrypted => {
            state.audit.write(AuditEvent {
                event_type: "message_denied".to_string(),
                room_id: room.room_id().to_string(),
                actor_id: event.sender.to_string(),
                operation_id: event.event_id.to_string(),
                route: "matrix".to_string(),
                result: "unencrypted_room".to_string(),
            })?;
        }
        ResponseDecision::Ignore => {}
        ResponseDecision::RespondCommand => {
            let Some(command) = command else {
                return Ok(());
            };
            match command {
                crate::commands::BridgeCommand::Pause => *state.paused.lock().await = true,
                crate::commands::BridgeCommand::Resume => *state.paused.lock().await = false,
                _ => {}
            }
            let paused = *state.paused.lock().await;
            room.send(RoomMessageEventContent::text_plain(command_response(
                command, paused,
            )))
            .await
            .context("send Matrix command response")?;
            state.audit.write(AuditEvent {
                event_type: "command_response".to_string(),
                room_id: room.room_id().to_string(),
                actor_id: event.sender.to_string(),
                operation_id: event.event_id.to_string(),
                route: "local".to_string(),
                result: "sent".to_string(),
            })?;
        }
        ResponseDecision::RespondLocal => match state.ollama.generate(&body).await {
            Ok(response) => {
                room.send(RoomMessageEventContent::text_plain(response))
                    .await
                    .context("send Matrix local model response")?;
                state.audit.write(AuditEvent {
                    event_type: "local_response".to_string(),
                    room_id: room.room_id().to_string(),
                    actor_id: event.sender.to_string(),
                    operation_id: event.event_id.to_string(),
                    route: "local".to_string(),
                    result: "sent".to_string(),
                })?;
            }
            Err(error) => {
                room.send(RoomMessageEventContent::text_plain(
                    "Local model request failed. Check the Hermes host logs.",
                ))
                .await
                .context("send Matrix Ollama failure response")?;
                state.audit.write(AuditEvent {
                    event_type: "local_response".to_string(),
                    room_id: room.room_id().to_string(),
                    actor_id: event.sender.to_string(),
                    operation_id: event.event_id.to_string(),
                    route: "local".to_string(),
                    result: format!("ollama_error:{error}"),
                })?;
            }
        },
    }

    Ok(())
}
