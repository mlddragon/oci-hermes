use hermes_bridge::ollama::{extract_ollama_response, OllamaError};

#[test]
fn extracts_response_text_from_ollama_json() {
    let body = r#"{"model":"local","response":"Hello from local Hermes","done":true}"#;

    let response = extract_ollama_response(body).unwrap();

    assert_eq!(response, "Hello from local Hermes");
}

#[test]
fn rejects_empty_ollama_response() {
    let body = r#"{"model":"local","response":"","done":true}"#;

    let error = extract_ollama_response(body).unwrap_err();

    assert!(matches!(error, OllamaError::EmptyResponse));
}
