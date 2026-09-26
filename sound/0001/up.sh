#!/bin/bash
set -e
mkdir -p ./audio_output
mkdir -p ./hf_cache
echo "🚀 Stopping existing containers..."
docker compose down || true
echo "📦 Starting SFX Generator..."
docker compose up -d --build
echo "✅ Container is running at http://localhost:8000"
echo "📋 Logs:"
docker compose logs -f