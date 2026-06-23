use std::fs;

use hermes_bridge::config::{BridgeConfig, ConfigError};
use tempfile::tempdir;

fn base_env(dir: &std::path::Path) -> Vec<(&'static str, String)> {
    let password_file = dir.join("matrix-password");
    fs::write(&password_file, "super-secret-password\n").unwrap();

    vec![
        (
            "HERMES_MATRIX_HOMESERVER_URL",
            "https://quiet-river-47.duckdns.org".to_string(),
        ),
        (
            "HERMES_MATRIX_USER_ID",
            "@hermes:quiet-river-47.duckdns.org".to_string(),
        ),
        (
            "HERMES_MATRIX_PASSWORD_FILE",
            password_file.display().to_string(),
        ),
        ("HERMES_MATRIX_DEVICE_NAME", "Hermes OCI Bridge".to_string()),
        (
            "HERMES_TRUSTED_INVITER_IDS",
            "@primary:quiet-river-47.duckdns.org,@admin:quiet-river-47.duckdns.org".to_string(),
        ),
        (
            "HERMES_BRIDGE_STORE_PATH",
            dir.join("store").display().to_string(),
        ),
        (
            "HERMES_AUDIT_LOG_PATH",
            dir.join("audit/events.jsonl").display().to_string(),
        ),
        ("OLLAMA_BASE_URL", "http://ollama:11434".to_string()),
        (
            "HERMES_LOCAL_MODEL",
            "hf.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF:Q4_K_M".to_string(),
        ),
        ("HERMES_OPENAI_ENABLED", "false".to_string()),
    ]
}

#[test]
fn loads_matrix_password_without_newline() {
    let dir = tempdir().unwrap();
    let config = BridgeConfig::from_pairs(base_env(dir.path())).unwrap();

    assert_eq!(
        config.matrix_password.expose_for_login(),
        "super-secret-password"
    );
}

#[test]
fn rejects_openai_enabled_for_this_slice() {
    let dir = tempdir().unwrap();
    let mut env = base_env(dir.path());
    for (key, value) in &mut env {
        if *key == "HERMES_OPENAI_ENABLED" {
            *value = "true".to_string();
        }
    }

    let error = BridgeConfig::from_pairs(env).unwrap_err();

    assert!(matches!(error, ConfigError::OpenAiEnabled));
}

#[test]
fn rejects_malformed_matrix_user_id() {
    let dir = tempdir().unwrap();
    let mut env = base_env(dir.path());
    for (key, value) in &mut env {
        if *key == "HERMES_MATRIX_USER_ID" {
            *value = "hermes".to_string();
        }
    }

    let error = BridgeConfig::from_pairs(env).unwrap_err();

    assert!(matches!(error, ConfigError::InvalidMatrixId { .. }));
}

#[test]
fn requires_at_least_one_trusted_inviter() {
    let dir = tempdir().unwrap();
    let mut env = base_env(dir.path());
    for (key, value) in &mut env {
        if *key == "HERMES_TRUSTED_INVITER_IDS" {
            *value = " ".to_string();
        }
    }

    let error = BridgeConfig::from_pairs(env).unwrap_err();

    assert!(matches!(error, ConfigError::MissingTrustedInviters));
}
