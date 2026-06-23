use std::{collections::HashMap, fs, path::PathBuf};

use ruma::{OwnedUserId, UserId};
use thiserror::Error;
use url::Url;

#[derive(Clone, Debug)]
pub struct PasswordSecret(String);

impl PasswordSecret {
    pub fn expose_for_login(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug)]
pub struct BridgeConfig {
    pub homeserver_url: Url,
    pub matrix_user_id: OwnedUserId,
    pub matrix_password: PasswordSecret,
    pub device_name: String,
    pub trusted_inviter_ids: Vec<OwnedUserId>,
    pub store_path: PathBuf,
    pub audit_log_path: PathBuf,
    pub ollama_base_url: Url,
    pub local_model: String,
}

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("missing required environment value {0}")]
    Missing(&'static str),
    #[error("invalid URL in {key}: {value}")]
    InvalidUrl { key: &'static str, value: String },
    #[error("invalid Matrix user id in {key}: {value}")]
    InvalidMatrixId { key: &'static str, value: String },
    #[error("Matrix password file could not be read: {0}")]
    PasswordFile(String),
    #[error("Matrix password file is empty")]
    EmptyPassword,
    #[error("HERMES_OPENAI_ENABLED must be false for this local-only bridge slice")]
    OpenAiEnabled,
    #[error("at least one trusted inviter is required")]
    MissingTrustedInviters,
}

impl BridgeConfig {
    pub fn from_env() -> Result<Self, ConfigError> {
        Self::from_pairs(std::env::vars())
    }

    pub fn from_pairs<I, K, V>(pairs: I) -> Result<Self, ConfigError>
    where
        I: IntoIterator<Item = (K, V)>,
        K: AsRef<str>,
        V: Into<String>,
    {
        let values: HashMap<String, String> = pairs
            .into_iter()
            .map(|(key, value)| (key.as_ref().to_string(), value.into()))
            .collect();

        let openai_enabled = get(&values, "HERMES_OPENAI_ENABLED")?;
        if openai_enabled.eq_ignore_ascii_case("true") {
            return Err(ConfigError::OpenAiEnabled);
        }

        let homeserver_url = parse_url(&values, "HERMES_MATRIX_HOMESERVER_URL")?;
        let matrix_user_id = parse_user_id(&values, "HERMES_MATRIX_USER_ID")?;
        let password_file = PathBuf::from(get(&values, "HERMES_MATRIX_PASSWORD_FILE")?);
        let matrix_password = fs::read_to_string(&password_file)
            .map_err(|error| ConfigError::PasswordFile(error.to_string()))?
            .trim()
            .to_string();
        if matrix_password.is_empty() {
            return Err(ConfigError::EmptyPassword);
        }

        let trusted_inviter_ids = values
            .get("HERMES_TRUSTED_INVITER_IDS")
            .map(String::as_str)
            .unwrap_or_default()
            .split(',')
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(|value| {
                UserId::parse(value).map_err(|_| ConfigError::InvalidMatrixId {
                    key: "HERMES_TRUSTED_INVITER_IDS",
                    value: value.to_string(),
                })
            })
            .collect::<Result<Vec<_>, _>>()?;
        if trusted_inviter_ids.is_empty() {
            return Err(ConfigError::MissingTrustedInviters);
        }

        Ok(Self {
            homeserver_url,
            matrix_user_id,
            matrix_password: PasswordSecret(matrix_password),
            device_name: get(&values, "HERMES_MATRIX_DEVICE_NAME")?,
            trusted_inviter_ids,
            store_path: PathBuf::from(get(&values, "HERMES_BRIDGE_STORE_PATH")?),
            audit_log_path: PathBuf::from(get(&values, "HERMES_AUDIT_LOG_PATH")?),
            ollama_base_url: parse_url(&values, "OLLAMA_BASE_URL")?,
            local_model: get(&values, "HERMES_LOCAL_MODEL")?,
        })
    }
}

fn get(values: &HashMap<String, String>, key: &'static str) -> Result<String, ConfigError> {
    values
        .get(key)
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
        .ok_or(ConfigError::Missing(key))
}

fn parse_url(values: &HashMap<String, String>, key: &'static str) -> Result<Url, ConfigError> {
    let value = get(values, key)?;
    Url::parse(&value).map_err(|_| ConfigError::InvalidUrl { key, value })
}

fn parse_user_id(
    values: &HashMap<String, String>,
    key: &'static str,
) -> Result<OwnedUserId, ConfigError> {
    let value = get(values, key)?;
    UserId::parse(&value).map_err(|_| ConfigError::InvalidMatrixId { key, value })
}
