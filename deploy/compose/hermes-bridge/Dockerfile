FROM python:3.12-slim

WORKDIR /app
COPY bridge.py /app/bridge.py

RUN useradd --system --home /var/lib/hermes-bridge --create-home hermes
USER hermes

CMD ["python", "/app/bridge.py"]
