from typing import Dict
from managers.llm_manager import LLMManager
from managers.file_manager import FileManager
from managers.token_manager import TokenManager
from managers.prompt_manager import PromptManager
from utils.utils import Utils
class CoreAgent:
    def __init__(self, model_name: str, src_path: str, app_data_path = None):
        self.src_path = src_path
        if app_data_path is None:
            app_data_path = Utils.get_app_data_path(src_path)
        
        Utils.check_file_exists(app_data_path) # if not exist raise error
        self.file_manager = FileManager(src_path, app_data_path)
        llm_manager = LLMManager()
        self.llm_model = llm_manager.create_model_instance_by_name(model_name)
        self.mapping_data = self.file_manager.get_mapping_data()
        self.sammry_data = self.file_manager.read_summary()
        self.token_manager = TokenManager(self.llm_model)
    
    def run_core_process(self, user_query: str) -> str:
        prompt_manager = PromptManager()
        result = self.find_relevant_files(user_query, prompt_manager)
        if not result:
            return "No relevant files found"
        
        return result
    
    def find_relevant_files(self, user_query: str, prompt_manager: PromptManager) -> list:
        """
        Find relevant files based on user query by processing data in chunks that fit token limits
        Returns a list of relevant file paths
        """
        all_relevant_files = []
        remaining_items = self.mapping_data.copy()
        selected_items = dict()
        
        while remaining_items:
            selected_items, remaining_items = self.token_manager.get_possible_data(
                user_query, 
                remaining_items
            )
            search_chain = prompt_manager.create_mappint_searcher_promtp_chain(self.llm_model)
            result = search_chain.invoke(input={
                "user_query": user_query, 
                "mapping_data": selected_items
            })
            list_of_files = result['files']
            if list_of_files:
                all_relevant_files.extend(list_of_files)
           
            
        
        # Remove duplicates while preserving order
        if not all_relevant_files:
            return []
        return self.file_manager.verify_files_list_paths(all_relevant_files)

    
    
if __name__ == "__main__":
    core_agent = CoreAgent(model_name="azure", src_path=r"C:\CodeAce\managers")
    user_query = "write all the files in the JSON"
    print(core_agent.run_core_process(user_query))