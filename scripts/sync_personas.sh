#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Pulling latest repo changes..."
git pull

echo "Rebuilding Ollama persona models..."
python3 scripts/create_ollama_personas.py

echo "Done."
