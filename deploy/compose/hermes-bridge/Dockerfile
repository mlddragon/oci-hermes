FROM rust:latest AS builder

WORKDIR /app
ENV CARGO_BUILD_JOBS=1
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release --locked

FROM debian:bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/hermes-bridge /usr/local/bin/hermes-bridge

CMD ["/usr/local/bin/hermes-bridge"]
