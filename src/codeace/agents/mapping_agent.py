import json
import os
from ..managers.llm_manager import LLMManager
from ..managers.file_manager import FileManager
from ..managers.prompt_manager import PromptManager
from ..utils.utils import Utils
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict

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
            app_data_path = Utils.get_app_data_path(src_path)
        
        self.app_data_path = app_data_path
        self.file_manager = FileManager(src_path, app_data_path)
        self.unmapped_files = []

    def run_mapping_process(self, ovveride: bool = False, generate_summery = True):
        """
        Main function to run the entire mapping process:
        1. Scan source directory
        2. Process each file
        3. Save mapping results

        Yields:
            str: Status message for each file being processed
        """
        
        # Get all relevant files from FileManager
        code_files = self.file_manager.scan_directory()
        
        if not ovveride and os.path.exists(self.file_manager.main_json_path):
            exist_mapped = self.file_manager.get_mapped_files()
            code_files = [file for file in code_files if file not in exist_mapped]
        
        # Process each file
        for file_path in code_files:
            try:
                current_index = code_files.index(file_path)
                status_message = f"Processing {current_index + 1}/{len(code_files)}: {os.path.basename(file_path)}"
                yield status_message
                
                self.process_single_file(file_path, generate_summery)
            except Exception as e:
                error_message = f"Error processing file {file_path}: {str(e)}"
                yield error_message
                self.unmapped_files.append(file_path)
                continue

        yield f"Mapping process completed. {len(self.unmapped_files)} files could not be processed."
        for file in self.unmapped_files:
            yield f"Unmapped file: {file}"
    
    def process_single_file(self, file_path: str, generate_summery = True) -> None:
        """
        Process a single file and save mapping results
        """
        try:
            # Get file content from FileManager
            content = self.file_manager.read_file(file_path)
            
            # Generate description using LLM
            description = self._generate_file_description(content, file_path)
            
            if generate_summery:
                # Generate summary using LLM
                self._generate_summary(content, file_path)

            # Create mapping structure
            mapping_data = self._create_mapping_structure(file_path,description)
            
            # Save mapping using FileManager
            self.file_manager.save_mapping(mapping_data)

        except Exception as e:
            raise e
            

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
    
    # TODO - Is this function needed?
    def _create_mapping_structure(self, 
                                file_path: str, 
                                description: Dict) -> dict:
        """
        Create standardized mapping structure to save in JSON
        """
        # save file_path to relative path from src_path
        file_path = os.path.relpath(file_path, self.src_path)
        return { 
            "file_name": file_path,
            "description": description["description"],
            "functions": description["functions"],
        }
    


if __name__ == "__main__":
    agent = MappingAgent(
        model_name="azure",
        src_path=r"C:\CodeAce\src\codeace\agents",
    )
    for status in agent.run_mapping_process():
        print(status)