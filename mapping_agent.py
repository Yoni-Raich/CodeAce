import json
import os
from managers.llm_manager import LLMManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
from managers.file_manager import FileManager
from managers.prompt_manager import PromptManager
from utils.utils import Utils
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
            app_data_path = Utils.get_app_data_path(src_path)
        
        self.app_data_path = app_data_path
        self.file_manager = FileManager(src_path, app_data_path)
        self.unmapped_files = []

    def run_mapping_process(self, ovveride: bool = False) -> None:
        """
        Main function to run the entire mapping process:
        1. Scan source directory
        2. Process each file
        3. Save mapping results
        """
        
        # Get all relevant files from FileManager
        code_files = self.file_manager.scan_directory()
        
        if not ovveride and os.path.exists(self.file_manager.main_json_path):
            exist_mapped = self.file_manager.get_mapped_files()
            code_files = [file for file in code_files if file not in exist_mapped]
        
        # Process each file
        for file_path in code_files:
            try:
                Utils.print_processing_message(file_path, len(code_files), code_files.index(file_path))
                self.process_single_file(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                self.unmapped_files.append(file_path)
                continue

            print(f"Mapping process completed. {len(self.unmapped_files)} files could not be processed.")
            for file in self.unmapped_files:
                print(f"Unmapped file: {file}")
    
    def process_single_file(self, file_path: str) -> None:
        """
        Process a single file and save mapping results
        """
        try:
            # Get file content from FileManager
            content = self.file_manager.read_file(file_path)
            
            # Generate description using LLM
            description = self._generate_file_description(content, file_path)
            
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