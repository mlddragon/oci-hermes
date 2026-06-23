use crate::commands::BridgeCommand;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum RoomKind {
    Direct,
    Group,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct MessageContext {
    pub encrypted: bool,
    pub paused: bool,
    pub mentions_hermes: bool,
    pub command: Option<BridgeCommand>,
    pub room_kind: RoomKind,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ResponseDecision {
    RespondCommand,
    RespondLocal,
    DenyUnencrypted,
    Ignore,
}

pub fn decide_response(context: MessageContext) -> ResponseDecision {
    if !context.encrypted {
        return ResponseDecision::DenyUnencrypted;
    }

    if context.command.is_some() {
        return ResponseDecision::RespondCommand;
    }

    if context.paused {
        return ResponseDecision::Ignore;
    }

    match context.room_kind {
        RoomKind::Direct => ResponseDecision::RespondLocal,
        RoomKind::Group if context.mentions_hermes => ResponseDecision::RespondLocal,
        RoomKind::Group => ResponseDecision::Ignore,
    }
}
