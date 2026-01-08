# Multi-Model LLM Conversation

A LangChain-based system that enables multiple Ollama LLM models to have structured debates on various topics.

## Features

- **Multi-round debates** between different LLM models
- **Session-based chat history** management
- **Role-based personalities** (Economist, Technologist, etc.)

## Requirements

```
langchain>=0.1.0
langchain-ollama>=0.0.1
langchain-community>=0.0.1
python-dotenv>=1.0.0
```

## Configuration

Create a `.env` file with the following variables:

```env
URL_BASE_OLLAMA=http://localhost:11434
MODEL_NAME_OLLAMA_MISTRAL=mistral
MODEL_NAME_OLLAMA_GEMMA3=gemma3
```

## Usage

```python
from LlmConversation import run_multi_model_conversation

result = run_multi_model_conversation(
    topic="The impact of artificial intelligence on the job market",
    session_id="ai-debate-2024",
    rounds=2
)
```

## Adding New Models

Add new models to the `MODELS` dictionary:

```python
MODELS["new_model"] = ModelConfig(
    name="NEW_MODEL",
    llm=create_llm("MODEL_NAME_OLLAMA_NEW"),
    system_prompt="Your custom system prompt...",
    role="Your Role"
)
```
