## Chainlit-Ollama-Demo

## Setup

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

### Agent app (using Open AI agents)

```bash
chainlit run src/agent_app.py -w
```
