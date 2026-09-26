#!/bin/bash
set -e
echo "🔨 Building SFX Generator Docker image..."
docker compose build --no-cache
echo "✅ Build completed successfully!"