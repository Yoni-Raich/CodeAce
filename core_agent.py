from typing import Dict, Tuple
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
        relevant_files_list = self.find_relevant_files(user_query, prompt_manager)
        if not relevant_files_list:
            return "No relevant files found"
        
        last_respond = self.process_code_query(user_query, relevant_files_list)
        return last_respond
    
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
    
    def process_code_query(self, user_query: str, file_paths: list) -> str:
        """
        Process a user query about specific code files.
        
        Args:
            user_query (str): The user's question about the code
            file_paths (list): List of relevant file paths to analyze
            
        Returns:
            str: The response to the user's query
        """
        remaining_files = file_paths
        previous_response = ""
        final_response = []
        
        prompt_manager = PromptManager()
        query_chain = prompt_manager.create_code_query_chain(self.llm_model)
        
        while remaining_files:
            # Get next batch of file contents
            content_chunk, remaining_files = self._get_next_content_chunk(user_query, remaining_files)
            if not content_chunk:
                break
            
            # Get LLM response for current chunk
            result = self._process_content_chunk(
                query_chain, 
                prompt_manager,
                content_chunk, 
                user_query, 
                previous_response, 
                bool(remaining_files)
            )
            
            final_response.append(result)
            previous_response = result
        
        return self._format_final_response(final_response)

    def _get_next_content_chunk(self, user_query: str, remaining_files: list) -> Tuple[str, list]:
        """Gets the next chunk of file contents that fits within token limits"""
        return self.token_manager.get_possible_files_content(user_query, remaining_files)

    def _process_content_chunk(
        self, 
        chain, 
        prompt_manager: PromptManager,
        content: str, 
        query: str, 
        previous_response: str, 
        has_remaining_files: bool
    ) -> str:
        """Processes a single chunk of content through the LLM"""
        context = prompt_manager.prepare_query_context(previous_response, has_remaining_files)
        
        return chain.invoke({
            "code_content": content,
            "user_query": query,
            **context
        })

    def _format_final_response(self, responses: list) -> str:
        """Formats the final response from all chunks"""
        if not responses:
            return "Could not process any files due to token limitations or file access issues."
        return responses[-1]

    
    
if __name__ == "__main__":
    core_agent = CoreAgent(model_name="azure", src_path=r"C:\CodeAce\managers")
    user_query = "'תכתוב סקריפט של בוט בממשק CLI המשתמש יכניס בהתחלה את שם המודל שהוא רוצה להשתמש ואז יתממשק עם הצאט דרך CLI'"
    print(core_agent.run_core_process(user_query))