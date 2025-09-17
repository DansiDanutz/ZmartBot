# Lightweight wrapper; the Cipher server runs via npx
FROM node:20

WORKDIR /srv/cipher

# Optional: install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Default command is set in compose
