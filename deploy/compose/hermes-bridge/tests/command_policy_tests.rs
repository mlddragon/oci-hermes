use hermes_bridge::{
    commands::{parse_command, BridgeCommand},
    policy::{decide_response, MessageContext, ResponseDecision, RoomKind},
};

#[test]
fn parses_supported_commands_case_insensitively() {
    assert_eq!(parse_command("!hermes status"), Some(BridgeCommand::Status));
    assert_eq!(parse_command("!Hermes pause"), Some(BridgeCommand::Pause));
    assert_eq!(parse_command("!hermes resume"), Some(BridgeCommand::Resume));
    assert_eq!(parse_command("!hermes help"), Some(BridgeCommand::Help));
}

#[test]
fn ignores_unknown_commands() {
    assert_eq!(parse_command("!hermes delete everything"), None);
    assert_eq!(parse_command("hello hermes"), None);
}

#[test]
fn direct_encrypted_room_responds_by_default() {
    let context = MessageContext {
        encrypted: true,
        paused: false,
        mentions_hermes: false,
        command: None,
        room_kind: RoomKind::Direct,
    };

    assert_eq!(decide_response(context), ResponseDecision::RespondLocal);
}

#[test]
fn group_encrypted_room_requires_mention_or_command() {
    let quiet_group = MessageContext {
        encrypted: true,
        paused: false,
        mentions_hermes: false,
        command: None,
        room_kind: RoomKind::Group,
    };
    let mentioned_group = MessageContext {
        mentions_hermes: true,
        ..quiet_group
    };

    assert_eq!(decide_response(quiet_group), ResponseDecision::Ignore);
    assert_eq!(
        decide_response(mentioned_group),
        ResponseDecision::RespondLocal
    );
}

#[test]
fn unencrypted_room_is_denied() {
    let context = MessageContext {
        encrypted: false,
        paused: false,
        mentions_hermes: true,
        command: None,
        room_kind: RoomKind::Direct,
    };

    assert_eq!(decide_response(context), ResponseDecision::DenyUnencrypted);
}
