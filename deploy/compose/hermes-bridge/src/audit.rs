use std::{
    fs::{self, OpenOptions},
    io::Write,
    path::PathBuf,
};

use chrono::{DateTime, Utc};
use serde::Serialize;
use sha2::{Digest, Sha256};

#[derive(Clone, Debug)]
pub struct AuditLogger {
    path: PathBuf,
}

#[derive(Clone, Debug)]
pub struct AuditEvent {
    pub event_type: String,
    pub room_id: String,
    pub actor_id: String,
    pub operation_id: String,
    pub route: String,
    pub result: String,
}

#[derive(Serialize)]
struct AuditRecord {
    timestamp: DateTime<Utc>,
    event_type: String,
    room_id_hash: String,
    actor_id_hash: String,
    operation_id: String,
    route: String,
    result: String,
}

impl AuditLogger {
    pub fn new(path: PathBuf) -> Self {
        Self { path }
    }

    pub fn write(&self, event: AuditEvent) -> std::io::Result<()> {
        if let Some(parent) = self.path.parent() {
            fs::create_dir_all(parent)?;
        }

        let record = AuditRecord {
            timestamp: Utc::now(),
            event_type: event.event_type,
            room_id_hash: hash_identifier(&event.room_id),
            actor_id_hash: hash_identifier(&event.actor_id),
            operation_id: event.operation_id,
            route: event.route,
            result: event.result,
        };
        let mut handle = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.path)?;
        writeln!(handle, "{}", serde_json::to_string(&record)?)?;
        Ok(())
    }
}

pub fn hash_identifier(value: &str) -> String {
    let digest = Sha256::digest(value.as_bytes());
    hex::encode(digest)
}
