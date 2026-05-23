# BA Copilot Core

Local-first AI tooling for business analysis, workshop facilitation, requirements gathering, and consulting-style delivery workflows.

This project combines:
- Ollama for local LLM inference
- Open WebUI for browser-based interaction
- Python tooling for structured BA workflows
- GitHub for prompt, template, and workflow versioning

The goal is to provide a reusable and private AI-assisted consulting environment that can support:
- workshop analysis
- requirements extraction
- RAID generation
- stakeholder analysis
- executive summaries
- process analysis
- project health assessments
- reusable delivery templates

---

# Architecture

Open WebUI
    ↓
Ollama
    ↓
Local LLMs
    ↓
BA Prompts / Personas / Templates

---

# Repository Structure

The repository is organised around reusable BA tooling, prompts, templates, and examples.

    ba-copilot-core/
    │
    ├── src/
    │   └── Python tooling and CLI scripts
    │
    ├── prompts/
    │   └── Reusable task prompts
    │
    ├── personas/
    │   └── System prompts and assistant personas
    │
    ├── templates/
    │   └── BA document templates
    │
    ├── docs/
    │   └── Internal documentation and setup notes
    │
    ├── examples/
    │   └── Sanitised example inputs
    │
    ├── outputs/
    │   └── Generated outputs, not committed
    │
    └── workspaces/
        └── Optional project or client workspaces

---
# Features

## Current

- Local LLM support via Ollama
- Open WebUI integration
- Prompt library for BA workflows
- Persona library for specialised assistants
- Markdown output generation
- Git-based version control
- Local-first and privacy-focused architecture

## Planned

- RAG / document retrieval
- Structured JSON output modes
- Jira / Confluence export
- Knowledge libraries
- Multi-workspace support
- Workflow automation
- Output validation

---

# Requirements

## macOS

The current setup has been tested on macOS.

## Software

Install:
- Python 3.10+
- Homebrew
- Docker Desktop
- Ollama
- Git

---

# Initial Setup

## 1. Clone Repository

git clone https://github.com/tom-yohan/ba-copilot-core.git
cd ba-copilot-core

---

## 2. Create Python Virtual Environment

python3 -m venv .venv
source .venv/bin/activate

---

## 3. Install Python Dependencies

pip install --upgrade pip setuptools
pip install -e .

---

## 4. Install Ollama

Install Ollama:
https://ollama.com/download

Or via Homebrew:

brew install ollama

Start Ollama:

brew services start ollama

---

## 5. Pull Local Models

ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull mistral:7b

---

## 6. Install Open WebUI

Ensure Docker Desktop is running.

docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart unless-stopped \
  openwebui/open-webui:latest

Open:
http://localhost:3000

---

# Using The Tooling

## Start Ollama

brew services start ollama

---

## Activate Python Environment

source .venv/bin/activate

---

## Run Healthcheck

PYTHONPATH=src python -m ba_copilot.main healthcheck

---

## Generate Outputs

### Executive Summary

PYTHONPATH=src python -m ba_copilot.main summarize examples/notes.md --output outputs/summary.md

### Requirements

PYTHONPATH=src python -m ba_copilot.main requirements examples/notes.md --output outputs/requirements.md

### RAID Log

PYTHONPATH=src python -m ba_copilot.main raid examples/notes.md --output outputs/raid.md

---

# Data Safety

This project is intended for local-first AI workflows.

Do not commit:
- client data
- employer data
- credentials
- regulated information
- raw meeting transcripts
- confidential documents

Use sanitised examples where possible.

---

# Recommended Workflow

1. Capture notes
2. Remove sensitive information
3. Analyse notes locally using Open WebUI or CLI tooling
4. Review outputs manually
5. Save reusable prompts/templates into GitHub
6. Store project-specific work in isolated workspaces

---

# Long-Term Direction

This repository is intended to evolve into a reusable AI-assisted consulting and business analysis framework with:
- local AI inference
- reusable consulting workflows
- prompt engineering
- knowledge retrieval
- structured delivery accelerators
- project-specific workspaces
