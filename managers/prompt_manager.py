from typing import List, Dict, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence

class CodeFileAnalysis(BaseModel):
    """Schema for code file analysis output"""
    description: str = Field(description="A deep and clear description of what the file does or represents")
    functions: str = Field(description="Comma-separated list of function names implemented in the file")

class RelevantFiles(BaseModel):
    """Schema for relevant files output"""
    files: List[str] = Field(description="List of relevant file names that match the user query")

class PromptManager:
    """Manager class for handling different prompt templates"""
    
    def __init__(self):
        pass
        
    def create_mapping_chain(self, llm)-> RunnableSequence:
        """Creates a mapping chain combining prompt template, LLM, and parser"""
        # Initialize the JSON parser with our schema
        parser = JsonOutputParser(pydantic_object=CodeFileAnalysis)
        
        # Define the system prompt
        system_prompt = """You are an expert developer in the programming language specified by the user (default is C#). 
                                Your task is to analyze code files and provide detailed information about them. 
                                You have a deep understanding of software architecture, design patterns, 
                                and best practices in software development.

                                When assigning tags, focus exclusively on the specific functionality, feature, or domain that the code addresses. 
                                Ignore the type or purpose of the file (e.g., test, manager, helper) and concentrate on the core content and what it actually does or represents in terms of business logic or system functionality."""

        # Define the mapping prompt template
        mapping_prompt = PromptTemplate(
            template="""
                {system_prompt}

                Please analyze the following code file and provide the following information in JSON format:

                1. description: A deep and clear description of what the file does or represents
                2. functions: An array of function names implemented in the file in ONE line split by ',' 
                - Focus on the core content and purpose of the code, not the type of file it is.

                Here is the file:

                File name: {file_name}
                {file_content}

                {format_instructions}
                """,
            input_variables=["file_content"],
            partial_variables={
                "system_prompt": system_prompt,
                "format_instructions": parser.get_format_instructions()
            }
        )
        
        return mapping_prompt | llm | parser
    

    def create_summery_update_chain(self, llm)-> RunnableSequence:
        """Creates a mapping chain combining prompt template, LLM, and parser"""
         # Define a prompt template for updating the summary
        prompt_template = PromptTemplate(
            template=(
                "You are a professional technical writer. Your task is to maintain a comprehensive, "
                "cohesive, and natural language description of a software project. This description should "
                "explain the purpose, functionality, and structure of the project in simple terms for developers, "
                "managers, and stakeholders. It should not include code snippets.\n\n"
                "Below is the current project summary, followed by the content of a new file.\n\n"
                "1. **Read the existing project summary** to understand the overall context.\n"
                "2. **Incorporate relevant details** from the new file's content into the project summary.\n"
                "3. Ensure the updated summary is easy to read, written in natural language, and avoids code snippets.\n\n"
                "Current Project Summary:\n{existing_summary}\n\n"
                "New File:\n{file_name}\n\n"
                "File Content:\n{file_content}\n\n"
                "Updated Project Summary (natural language only):"
            ),
            input_variables=["existing_summary", "file_name", "file_content"],
        )

        # Combine the components: prompt template, LLM, and output parser
        return prompt_template | llm | StrOutputParser()
    
    def create_mappint_searcher_promtp_chain(self, llm)-> RunnableSequence:
        """Creates a mapping chain combining prompt template, LLM, and parser"""
        # Initialize the JSON parser with our schema
        parser = JsonOutputParser(pydantic_object=RelevantFiles)
        
        # Define the search prompt template
        search_prompt = PromptTemplate(
            template="""You are an AI assistant designed to help users find relevant files in a codebase based on a summary JSON file. 
                When a user provides a query, analyze it and determine which files are most likely relevant.
                
                The JSON data contains file information in this format:
                [
                    {{
                        "file_name": "path/to/file",
                        "description": "description of the file",
                        "functions": "func1,func2,..."
                    }},
                    ...
                ]

                User Query: {user_query}
                Available Files Data: {mapping_data}

                Return ONLY the most relevant files that can be related to the user query.
                Focus on the file paths that are most relevant to solving the user's query.
                {format_instructions}
                """,
            input_variables=["user_query", "mapping_data"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )
        
        # Combine the components: prompt template, LLM, and parser
        return search_prompt | llm | parser

if __name__ == "__main__":
    prompt_manager = PromptManager()
    prompt_template = PromptTemplate(
            template=(
                "You are a professional technical writer. Your task is to maintain a comprehensive, "
                "cohesive, and natural language description of a software project. This description should "
                "explain the purpose, functionality, and structure of the project in simple terms for developers, "
                "managers, and stakeholders. It should not include code snippets.\n\n"
                "Below is the current project summary, followed by the content of a new file.\n\n"
                "1. **Read the existing project summary** to understand the overall context.\n"
                "2. **Incorporate relevant details** from the new file's content into the project summary.\n"
                "3. Ensure the updated summary is easy to read, written in natural language, and avoids code snippets.\n\n"
                "Current Project Summary:\n{existing_summary}\n\n"
                "New File:\n{file_name}\n\n"
                "File Content:\n{file_content}\n\n"
                "Updated Project Summary (natural language only):"
            ),
            input_variables=["existing_summary", "file_name", "file_content"],
        )
    