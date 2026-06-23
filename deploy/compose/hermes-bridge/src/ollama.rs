use reqwest::Url;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum OllamaError {
    #[error("Ollama request failed: {0}")]
    Request(String),
    #[error("Ollama returned invalid JSON: {0}")]
    InvalidJson(String),
    #[error("Ollama returned an empty response")]
    EmptyResponse,
}

#[derive(Serialize)]
struct GenerateRequest<'a> {
    model: &'a str,
    prompt: &'a str,
    stream: bool,
}

#[derive(Deserialize)]
struct GenerateResponse {
    response: String,
}

#[derive(Clone)]
pub struct OllamaClient {
    http: reqwest::Client,
    base_url: Url,
    model: String,
}

impl OllamaClient {
    pub fn new(base_url: Url, model: String) -> Self {
        Self {
            http: reqwest::Client::new(),
            base_url,
            model,
        }
    }

    pub async fn generate(&self, prompt: &str) -> Result<String, OllamaError> {
        let url = self
            .base_url
            .join("/api/generate")
            .map_err(|error| OllamaError::Request(error.to_string()))?;
        let response = self
            .http
            .post(url)
            .json(&GenerateRequest {
                model: &self.model,
                prompt,
                stream: false,
            })
            .send()
            .await
            .map_err(|error| OllamaError::Request(error.to_string()))?;
        let body = response
            .text()
            .await
            .map_err(|error| OllamaError::Request(error.to_string()))?;
        extract_ollama_response(&body)
    }
}

pub fn extract_ollama_response(body: &str) -> Result<String, OllamaError> {
    let parsed: GenerateResponse =
        serde_json::from_str(body).map_err(|error| OllamaError::InvalidJson(error.to_string()))?;
    let response = parsed.response.trim().to_string();
    if response.is_empty() {
        return Err(OllamaError::EmptyResponse);
    }
    Ok(response)
}
