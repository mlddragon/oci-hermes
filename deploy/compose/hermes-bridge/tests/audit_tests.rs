use std::fs;

use hermes_bridge::audit::{AuditEvent, AuditLogger};
use tempfile::tempdir;

#[test]
fn audit_log_hashes_identifiers_and_omits_message_content() {
    let dir = tempdir().unwrap();
    let log_path = dir.path().join("audit.jsonl");
    let logger = AuditLogger::new(log_path.clone());

    logger
        .write(AuditEvent {
            event_type: "local_response".to_string(),
            room_id: "!room:quiet-river-47.duckdns.org".to_string(),
            actor_id: "@primary:quiet-river-47.duckdns.org".to_string(),
            operation_id: "op-123".to_string(),
            route: "local".to_string(),
            result: "allowed".to_string(),
        })
        .unwrap();

    let contents = fs::read_to_string(log_path).unwrap();

    assert!(contents.contains("\"event_type\":\"local_response\""));
    assert!(contents.contains("\"room_id_hash\""));
    assert!(contents.contains("\"actor_id_hash\""));
    assert!(!contents.contains("!room:quiet-river-47.duckdns.org"));
    assert!(!contents.contains("@primary:quiet-river-47.duckdns.org"));
    assert!(!contents.contains("hello hermes"));
}
