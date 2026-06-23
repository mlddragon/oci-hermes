#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BridgeCommand {
    Status,
    Pause,
    Resume,
    Help,
}

pub fn parse_command(body: &str) -> Option<BridgeCommand> {
    let normalized = body.trim().to_ascii_lowercase();
    match normalized.as_str() {
        "!hermes status" => Some(BridgeCommand::Status),
        "!hermes pause" => Some(BridgeCommand::Pause),
        "!hermes resume" => Some(BridgeCommand::Resume),
        "!hermes help" => Some(BridgeCommand::Help),
        _ => None,
    }
}

pub fn command_response(command: BridgeCommand, paused: bool) -> &'static str {
    match command {
        BridgeCommand::Status if paused => "Hermes bridge is paused. Local routing is available after !hermes resume.",
        BridgeCommand::Status => "Hermes bridge is running in local-only mode. OpenAI routing is disabled.",
        BridgeCommand::Pause => "Hermes bridge paused for this process.",
        BridgeCommand::Resume => "Hermes bridge resumed.",
        BridgeCommand::Help => {
            "Commands: !hermes status, !hermes pause, !hermes resume, !hermes help. OpenAI routing is disabled in this slice."
        }
    }
}
