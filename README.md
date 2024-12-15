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
# Note: Mapping process automatically uses GPT-4o-mini for efficient processing
mapping_agent = MappingAgent(model_name=model_name, src_path=src_path)
mapping_agent.run_mapping_process()

# Query your code (uses full model capabilities)
core_agent = CoreAgent(model_name=model_name, src_path=src_path)
result = core_agent.run_core_process("Explain how the error handling works in this codebase")
print(result)
```

## Advanced Usage

### Mapping Process

The mapping process uses Azure OpenAI's GPT-4o-mini model for optimal performance and cost efficiency. This process:
- Scans your codebase
- Analyzes each file
- Generates descriptions and function lists
- Creates a searchable index
- Builds a project summary

```python
# Initialize mapping agent
mapping_agent = MappingAgent(model_name="azure", src_path=src_path)

# Run mapping with progress updates
for status in mapping_agent.run_mapping_process():
    print(status)  # Shows progress of file processing

# Optional: Force remapping of all files
mapping_agent.run_mapping_process(override=True)

# Optional: Map without generating summary
mapping_agent.run_mapping_process(generate_summary=False)
```

### Context Management

CodeAce supports rich context management to improve code analysis:

```python
# Initialize agent
core_agent = CoreAgent(model_name="azure", src_path=src_path)

# Add documentation context from file
core_agent.add_extra_context_by_path("path/to/documentation.md")

# Add custom context directly
core_agent.add_extra_context("Additional context information")

# Context is automatically used to improve prompts
improved_prompt = core_agent.improve_user_prompt(user_query)

# Context is considered during code analysis
result = core_agent.process_code_query(user_query, relevant_files)
```

### Multi-Codebase Analysis

You can analyze dependencies across multiple codebases:

```python
# Initialize agents for different codebases
main_agent = CoreAgent(model_name="azure", src_path=main_src)
modules_agent = CoreAgent(model_name="azure", src_path=modules_src)

# Analyze dependencies
dependencies_result = modules_agent.process_dependencies_query(query, files)

# Use dependencies context in main analysis
main_agent.add_extra_context(dependencies_result)
result = main_agent.process_code_query(query, files)
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
