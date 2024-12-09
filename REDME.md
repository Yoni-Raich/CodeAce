# Mapping Agent

The `MappingAgent` class is designed to automate the process of scanning a source directory, analyzing code files using a Large Language Model (LLM), and generating detailed descriptions and summaries for each file. The results are saved in a JSON file and a markdown summary document.

## Features

- **Initialization**: Sets up the necessary components, including the LLM model, file manager, and prompt manager.
- **Directory Scanning**: Recursively scans the specified source directory to identify relevant code files.
- **File Processing**: Processes each file to generate descriptions and summaries using the LLM.
- **Mapping Management**: Saves the generated descriptions and summaries in a JSON file and a markdown document.

## Usage

### Initialization

To initialize the `MappingAgent`, provide the LLM model name, source code path, and optionally the output path for JSON files.

```python
agent = MappingAgent(
    model_name="gemini",
    src_path=r"C:\CodeAce\managers",
)