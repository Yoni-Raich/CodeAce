import os
import json
from typing import List, Dict
from pathlib import Path

class FileManager:
    def __init__(self, src_path: str, app_data_path: str):
        """
        Initialize FileManager with source and output paths
        """
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source path not found: {src_path}")
        self.src_path = src_path
        self.app_data_path = app_data_path
        self._create_app_data_dir()
        self.main_json_path = os.path.join(self.app_data_path, "code_mapping.json")
        self.summary_doc_path = os.path.join(self.app_data_path, "summary_doc.md")
        self._initialize_main_json()
    
    def _initialize_main_json(self) -> None:
        """Initialize the main JSON file if it doesn't exist"""
        if not os.path.exists(self.main_json_path):
            with open(self.main_json_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _create_app_data_dir(self) -> None:
        """Create app_data directory if it doesn't exist"""
        os.makedirs(self.app_data_path, exist_ok=True)

    def scan_directory(self) -> List[str]:
        """
        Recursively scan directory and return list of code files
        """
        code_files = []
        excluded_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.env'}
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.cs', '.rb', '.go'}

        for root, dirs, files in os.walk(self.src_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if Path(file).suffix in code_extensions:
                    full_path = os.path.join(root, file)
                    code_files.append(full_path)
        
        return code_files

    def read_file(self, path: str) -> str:
        """
        Read and return file content
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                if not content:
                    raise ValueError(f"File {path} is empty")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at path: {path}")
        except IOError as e:
            raise IOError(f"Error reading file at {path}: {str(e)}")

    def save_mapping(self, mapping_data: Dict) -> None:
        """
        Add or update mapping data in the main JSON file
        """
        try:
            # Read existing mappings
            with open(self.main_json_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            
            # Check if file already exists in mappings
            file_path = mapping_data.get('file_name')
            existing_index = next(
                (index for (index, d) in enumerate(mappings) 
                if d.get('file_name') == file_path),
                None
            )
            
            # Update existing or append new
            if existing_index is not None:
                mappings[existing_index] = mapping_data
            else:
                mappings.append(mapping_data)
            
            # Write back to file
            with open(self.main_json_path, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, indent=2)
                
        except IOError as e:
            raise IOError(f"Error updating mapping file at {self.main_json_path}: {str(e)}")

    def get_mapped_files(self) -> List[str]:
        """
        Get list of mapped files from main JSON file
        """
        try:
            with open(self.main_json_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                return [m['file_name'] for m in mappings]
        except FileNotFoundError:
            return []
        except IOError as e:
            raise IOError(f"Error reading mapping file at {self.main_json_path}: {str(e)}")

    def save_summary(self, summary: str) -> None:
        """
        Save summary to a markdown file
        """
        try:
            with open(self.summary_doc_path, 'w', encoding='utf-8') as f:
                f.write(summary)
        except IOError as e:
            raise IOError(f"Error saving summary to {self.summary_doc_path}: {str(e)}")
    
    def read_summary(self) -> str:
        """
        Read and return summary content
        """
        try:
            with open(self.summary_doc_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            with open(self.summary_doc_path, 'w', encoding='utf-8') as file:
                file.write("This document contains summaries of the codebase files.")
        except IOError as e:
            raise IOError(f"Error reading file at {self.summary_doc_path}: {str(e)}")

#Tests...
if __name__ == "__main__":
    file_m = FileManager(r"C:\CodeAce",r"C:\CodeAce\CodeAceData")
    files_list = file_m.scan_directory()
    print(file_m.read_file(files_list[0]))