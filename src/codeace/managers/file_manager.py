import os
import json
from typing import List, Dict
from pathlib import Path
from PyPDF2 import PdfReader


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
    
    def read_extra_context_doc(self, extra_context_doc_path: str) -> str:
        """
        Read and return extra context document content, supporting both text and PDF files
        """
        if not extra_context_doc_path:
            extra_context_doc_path = self.summary_doc_path
        
        if extra_context_doc_path.endswith('.pdf'):
            content = self.read_pdf_file(extra_context_doc_path)
        else:
            content = self.read_file(extra_context_doc_path)
        
        return content

    def read_pdf_file(self, path: str) -> str:
        """
        Read and return text content from a PDF file
        """
        try:
            with open(path, 'rb') as file:
                reader = PdfReader(file)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
                if not content:
                    raise ValueError(f"PDF file {path} is empty or unreadable")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found at path: {path}")
        except Exception as e:
            raise IOError(f"Error reading PDF file at {path}: {str(e)}")

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
    
    def get_mapping_data(self) -> Dict:
        """
        Get mapping data from main JSON file
        """
        try:
            with open(self.main_json_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                return mappings
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

    def get_summary_data(self) -> str:
        """
        Get summary data from markdown file
        """
        try:
            with open(self.summary_doc_path, 'r', encoding='utf-8') as f:
                summary = f.read()
                return summary
        except IOError as e:
            raise IOError(f"Error reading summary file at {self.summary_doc_path}: {str(e)}")

    def verify_files_list_paths(self, file_paths: List[str]) -> List[str]:
        """
        Verify and correct file paths in the given list.
        If a path doesn't exist, searches for the file by name in the source directory.
        Returns a list of corrected paths, removing invalid ones.
        
        Args:
            file_paths: List of file paths to verify
            
        Returns:
            List of verified and corrected file paths
        """
        verified_paths = []
        
        for file_path in file_paths:
            file_path = os.path.join(self.src_path, file_path)
            if os.path.exists(file_path):
                verified_paths.append(file_path)
            else:
                # Get just the filename from the path
                file_name = os.path.basename(file_path)
                
                # Search for the file in the source directory
                found = False
                for root, _, files in os.walk(self.src_path):
                    if file_name in files:
                        new_path = os.path.join(root, file_name)
                        verified_paths.append(new_path)
                        found = True
                        break
                        
                # If file wasn't found, it will be skipped
        # Filter out duplicates
        verified_paths = list(dict.fromkeys(verified_paths))
        return verified_paths

#Tests...
if __name__ == "__main__":
    file_m = FileManager(r"C:\CodeAce",r"C:\CodeAce\CodeAceData")
    files_list = file_m.scan_directory()
    print(file_m.read_file(files_list[0]))