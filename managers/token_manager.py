import json
import tiktoken  # For OpenAI tokenization
from typing import Any, Dict, Tuple


class TokenManager:
    """
    A utility class for managing token usage in LLM-based applications.
    Supports OpenAI and Hugging Face models, with the ability to calculate
    token usage and manage input limits.
    """

    def __init__(self, llm: Any):
        """
        Initialize the TokenManager with an LLM instance.

        Args:
            llm (Any): An LLM instance (e.g., OpenAI, Hugging Face, or custom).
        """
        self.llm = llm
        self.tokenizer, self.max_tokens = self._get_tokenizer_and_limits()

    def _get_tokenizer_and_limits(self) -> Tuple[Any, int]:
        """
        Identify the tokenizer and maximum token limit for the LLM.

        Returns:
            Tuple[Any, int]: The tokenizer and maximum token limit.
        """
        
        encoding = tiktoken.encoding_for_model(self.llm.model_name)
        max_tokens = self.llm.max_tokens
        return encoding, max_tokens
        
       

    def calculate_tokens(self, text: str) -> int:
        """
        Calculate the number of tokens in a given text.

        Args:
            text (str): The input text.

        Returns:
            int: The number of tokens in the text.
        """
        if isinstance(self.tokenizer, tiktoken.Encoding):
            return len(self.tokenizer.encode(text))
        
    def get_possible_data(self, user_query: str, json_data: list) -> Tuple[list, list]:
        """
        Select items from a JSON array based on token constraints.

        Args:
            prompt_template (str): The template to be used with the data
            user_query (str): The user's query
            json_data (list): List of dictionaries containing file information

        Returns:
            Tuple[list, list]: Selected items and remaining items
        """
        user_query_tokens = self.calculate_tokens(f"{user_query}")
        remaining_tokens = self.max_tokens - user_query_tokens

        added_tokens = 0
        selected_items = []
        remaining_items = json_data.copy()
        
        for item in json_data:
            # Calculate tokens for the entire item
            item_str = f"file_name: {item['file_name']}\nDescription: {item['description']}\nFunctions: {item['functions']}"
            item_tokens = self.calculate_tokens(item_str)
            
            if added_tokens + item_tokens <= remaining_tokens:
                selected_items.append(remaining_items.pop(0))
                added_tokens += item_tokens
            else:
                break
                
        return selected_items, remaining_items

    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate if a given prompt fits within the model's token constraints.

        Args:
            prompt (str): The prompt to validate.

        Returns:
            bool: True if the prompt is valid, False otherwise.
        """
        prompt_tokens = self.calculate_tokens(prompt)
        return prompt_tokens <= self.max_tokens


# Example Usage
if __name__ == "__main__":
    # Example: OpenAI model
    from llm_manager import LLMManager
    llm_manager = LLMManager()
    llm_openai = llm_manager.create_model_instance_by_name("azure")
    token_manager = TokenManager(llm_openai)

    user_query = "What is the weather in Tel Aviv today?"
    json_data = {"temperature": "25°C", "humidity": "60%", "condition": "Clear skies"}
    print(token_manager.calculate_tokens(user_query))
