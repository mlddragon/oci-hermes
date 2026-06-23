use anyhow::Result;
use hermes_bridge::{config::BridgeConfig, matrix_runtime};

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    let config = BridgeConfig::from_env()?;
    matrix_runtime::run(config).await
}
