## Chainlit-Ollama-Demo

## Setup

### Install uv

Follow instructions: https://docs.astral.sh/uv/getting-started/installation/

### Install deps

```bash
uv venv
source .venv/bin/activate
uv sync
```

## Local server

### Simple app (Ollama only)

```bash
chainlit run src/simple_app.py -w
```

### Agent app (Ollama only)

```bash
chainlit run src/simple_agent_app.py -w
```

### Multi Agent app

```bash
chainlit run src/multi_agent_app.py -w
```
