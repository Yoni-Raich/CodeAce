# CodeAce

CodeAce is a Python package that helps you analyze and understand your codebase using Large Language Models (LLMs). It provides an intuitive interface to map your codebase and query it using natural language.

## Features

- 🤖 Multiple LLM providers support (Azure OpenAI, OpenAI, Google Gemini, Anthropic Claude)
- 🔍 Smart code search and analysis
- 💡 Natural language queries about your code
- 📝 Automatic code documentation

## Installation

```bash
pip install codeace
```

## Quick Start

```python
from dotenv import load_dotenv
from codeace import CoreAgent, MappingAgent

# Load environment variables
load_dotenv()

# Initialize agents
src_path = "path/to/your/code"
model_name = "azure"  # or "openai", "gemini", "anthropic"

# Map your codebase (do this once)
mapping_agent = MappingAgent(model_name=model_name, src_path=src_path)
mapping_agent.run_mapping_process()

# Query your code
core_agent = CoreAgent(model_name=model_name, src_path=src_path)
result = core_agent.run_core_process("Explain how the error handling works in this codebase")
print(result)
```

## Environment Setup

1. Create a `.env` file in your project root directory
2. Add the required environment variables based on your chosen LLM provider:

### OpenAI
```env
OPENAI_API_KEY=your_api_key_here
```

### Azure OpenAI
```env
AZ_OPENAI_API_KEY=your_azure_api_key_here
AZ_OPENAI_API_BASE=your_azure_endpoint_here
AZ_OPENAI_API_VERSION=your_api_version_here
AZ_OPENAI_LLM_4_O=your_deployment_name_here
```

### Google (Gemini)
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Anthropic
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```


## Supported LLM Providers

Choose the appropriate `model_name` when initializing agents:
- `"azure"`: Azure OpenAI (GPT-4o)
- `"openai"`: OpenAI API (GPT-4)
- `"gemini"`: Google Gemini Pro
- `"anthropic"`: Anthropic Claude
- `"ollama"`: Local Ollama models

## Requirements

- Python 3.8+
- Required dependencies (installed automatically):
  - langchain
  - pydantic
  - python-dotenv
  - tiktoken
  - (Provider-specific packages based on your choice)


- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Supports multiple LLM providers
