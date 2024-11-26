import json
import os
from managers.llm_manager import LLMManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
from managers.file_manager import FileManager
from managers.prompt_manager import PromptManager

# Example of how to use the LLMManager to generate text
# llm_manager = LLMManager()
# parser = JsonOutputParser(pydantic_object=MappingFile)
# llm = llm_manager._get_azure_openai_llm()
# promtp = prompt = PromptTemplate(
#     template="Answer the user query.\n{format_instructions}\n{query}\n",
#     input_variables=["query"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )

# chain = prompt | llm | parser
# js = chain.invoke(input={"query": "file path: c:\\user\\files\\hellofile.txt\n Hello to the world"})
class MappingAgent:
    def __init__(self, model_name: str, src_path: str, app_data_path: str = None):
        """
        Initialize the mapping agent with:
        - LLM model name - supported list (openai, azure, ollama, gemini, anthropic)
        - Source code path
        - Output path for JSON files
        - File manager instance
        """
        llm_manager = LLMManager()
        self.prompt_manager = PromptManager()
        self.llm_model = llm_manager.create_model_instance_by_name(model_name)
        self.src_path = src_path
        if not app_data_path:
            app_data_path = os.path.join(src_path, "CodeAce", "app_data")
        
        self.app_data_path = app_data_path
        self.file_manager = FileManager(src_path, app_data_path)

    def run_mapping_process(self) -> None:
        #TODO - create one main documenation for entire codebase
        """
        Main function to run the entire mapping process:
        1. Scan source directory
        2. Process each file
        3. Save mapping results
        """
        # Get all relevant files from FileManager
        code_files = self.file_manager.scan_directory()
        
        # Process each file
        for file_path in code_files:
            try:
                print(f"Processing file: {file_path} ...")
                # Get file content from FileManager
                content = self.file_manager.read_file(file_path)
                
                # Generate description using LLM
                description = self._generate_file_description(content, file_path)
                
                # Generate summary using LLM
                self._generate_summary(content, file_path)

                # Create mapping structure
                mapping_data = self._create_mapping_structure(
                    file_path=file_path,
                    description=description,
                )
                
                # Save mapping using FileManager
                self.file_manager.save_mapping(mapping_data)
                print(f"File {file_path} processed successfully.\n\n")
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                continue

    def _generate_file_description(self, content: str, file_path: str) -> Dict:
        """
        Use LLM to generate file description based on content
        Uses predefined prompt template
        """
        # Run LLM to generate description
        mapping_chain = self.prompt_manager.create_mapping_chain(self.llm_model)
        result = mapping_chain.invoke(input={'file_name': file_path, "file_content": content})

        return result
    def _generate_summary(self, content: str, file_path: str) -> None:
        """
        Use LLM to generate summary based on content
        """
        # Run summarization chain
        last_summary = self.file_manager.read_summary()
        summary_chain = self.prompt_manager.create_summery_update_chain(self.llm_model)
        summary = summary_chain.invoke(input={"existing_summary": last_summary,"file_name":file_path , "file_content":content})
        self.file_manager.save_summary(summary)

    def _create_mapping_structure(self, 
                                file_path: str, 
                                description: Dict) -> dict:
        """
        Create standardized mapping structure to save in JSON
        """
        return { 
            "file_name": file_path,
            "description": description["description"],
            "functions": description["functions"],
        }
    


if __name__ == "__main__":
    agent = MappingAgent(
        model_name="azure",
        src_path=r"C:\CodeAce\managers",
    )
    agent.run_mapping_process()