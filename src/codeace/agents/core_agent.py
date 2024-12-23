from typing import Dict, Tuple
from ..managers.llm_manager import LLMManager
from ..managers.file_manager import FileManager
from ..managers.token_manager import TokenManager
from ..managers.prompt_manager import PromptManager
from ..utils.utils import Utils
class CoreAgent:
    def __init__(self, model_name: str, src_path: str, app_data_path = None, extra_context_doc_path = None):
        """
        Initialize the core agent with:
        - LLM model name - supported list (openai, azure, ollama, gemini, anthropic)
        - Source code path
        - Optional: app_data_path for JSON files (if None, will be created automatically)
        """
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
        self.prompt_manager = PromptManager()
        self.extra_context_doc = self.file_manager.read_extra_context_doc(extra_context_doc_path)
        

    def run_core_process(self, user_query: str) -> str:
        relevant_files_list = self.find_relevant_files(user_query)
        if not relevant_files_list:
            return "No relevant files found"
        
        last_respond = self.process_code_query(user_query, relevant_files_list)
        return last_respond
    
    def find_relevant_files(self, user_query: str) -> list:
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
            search_chain = self.prompt_manager.create_mappint_searcher_promtp_chain(self.llm_model)
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
    
    def _process_code_query_logic(self, user_query: str, file_paths: list, query_chain) -> str:
        """
        Core logic for processing code queries.
        
        Args:
            user_query (str): The user's question about the code
            file_paths (list): List of relevant file paths to analyze
            query_chain: The chain to use for processing the query
            
        Returns:
            str: The response to the user's query
        """
        if not file_paths:
            return f"No relevant files found for query, will call the llm model with the query only.\n\n{self.llm_model.invoke(user_query).content}"

        remaining_files = file_paths
        previous_response = ""
        final_response = []
        
        while remaining_files:
            content_chunk, remaining_files = self._get_next_content_chunk(user_query, remaining_files)
            if not content_chunk:
                break
            
            result = self._process_content_chunk(
                query_chain, 
                content_chunk, 
                user_query, 
                previous_response, 
                bool(remaining_files)
            )
            
            final_response.append(result)
            previous_response = result
        
        return self._format_final_response(final_response)

    def process_code_query(self, user_query: str, file_paths: list) -> str:
        """
        Process a user query about specific code files.
        
        Args:
            user_query (str): The user's question about the code
            file_paths (list): List of relevant file paths to analyze
            
        Returns:
            str: The response to the user's query
        """
        query_chain = self.prompt_manager.create_code_query_chain(self.llm_model)
        return self._process_code_query_logic(user_query, file_paths, query_chain)

    def process_dependencies_query(self, user_query: str, file_paths: list) -> str:
        """
        Process a user query about code dependencies.
        
        Args:
            user_query (str): The user's question about the code
            file_paths (list): List of relevant file paths to analyze
            
        Returns:
            str: The response to the user's query
        """
        query_chain = self.prompt_manager.create_dependencies_analysis_chain(self.llm_model)
        return self._process_code_query_logic(user_query, file_paths, query_chain)
    
    
    def add_extra_context(self, extra_context_doc: str, override: bool = False) -> None:
        """
        Add extra context document to the agent.
        If override is True, the existing context will be replaced.
        """
        if override:
            self.extra_context_doc = extra_context_doc
        else:
            self.extra_context_doc = f"{self.extra_context_doc}\n{extra_context_doc}"
    #TODO - create a method to add the summary to the context
    def add_extra_context_by_path(self, extra_context_doc_path :str = None, override: bool = False) -> None:
        """
        Add extra context document to the agent.
        If override is True, the existing context will be replaced.
        """
        extra_context_doc = self.file_manager.read_extra_context_doc(extra_context_doc_path)
        self.add_extra_context(extra_context_doc, override)

    
    def _get_next_content_chunk(self, user_query: str, remaining_files: list) -> Tuple[str, list]:
        """Gets the next chunk of file contents that fits within token limits"""
        return self.token_manager.get_possible_files_content(user_query,self.extra_context_doc, remaining_files)

    def _process_content_chunk(
        self, 
        chain, 
        content: str, 
        query: str, 
        previous_response: str, 
        has_remaining_files: bool
    ) -> str:
        """Processes a single chunk of content through the LLM"""
        context = self.prompt_manager.prepare_query_context(previous_response, has_remaining_files)
        
        return chain.invoke({
            "context": self.extra_context_doc,
            "code_content": content,
            "user_query": query,
            **context
        })

    def _format_final_response(self, responses: list) -> str:
        """Formats the final response from all chunks"""
        if not responses:
            return "Could not process any files due to token limitations or file access issues."
        return responses[-1]

    def improve_user_prompt(self, user_query: str) -> str:
        """
        Improves the user's prompt by incorporating context from documentation
        and making it more structured for code generation.
        
        Args:
            user_query (str): The original user query/prompt
            
        Returns:
            str: An improved, more structured version of the prompt
        """
        improver_chain = self.prompt_manager.create_prompt_improver_chain(self.llm_model)
        
        # Combine project summary and extra context as documentation
        documentation = f"""Project Summary:
        {self.sammry_data}

        Additional Context:
        {self.extra_context_doc}"""
        
        improved_prompt = improver_chain.invoke({
            "documentation": documentation,
            "user_query": user_query
        })
        
        return improved_prompt