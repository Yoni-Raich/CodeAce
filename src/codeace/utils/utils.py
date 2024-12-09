import os

class Utils:
    
    @staticmethod
    def print_processing_message(current_file: str,max_iter: int, current_iter: int):
        print(f"Processing file: {current_file} - {current_iter}/{max_iter}...", end='\r')

    @staticmethod
    def get_app_data_path(src_path: str) -> str:
        """
        Get the application data path based on the source path.
        """
        return os.path.join(src_path, "CodeAce", "app_data")

    @staticmethod
    def check_file_exists(path: str) -> None:
        """
        Check if a file exists at the given path.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at path {path}")
