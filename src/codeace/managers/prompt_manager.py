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
        parser = JsonOutputParser(pydantic_object=RelevantFiles)
        
        # Updated search prompt to be more strict about relevance
        search_prompt = PromptTemplate(
            template="""You are an AI assistant helping users find relevant files in a codebase.
                Analyze the user query carefully - if it's just a greeting or doesn't contain a specific
                technical question or request, return an empty list of files.
                
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

                Return files ONLY if the query contains a specific technical question or request.
                For greetings or general conversation, return an empty list.
                {format_instructions}
                """,
            input_variables=["user_query", "mapping_data"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )
        
        return search_prompt | llm | parser

    def create_code_query_chain(self, llm) -> RunnableSequence:
        """Creates a chain for answering queries based on code content"""
        prompt_template = PromptTemplate(
            template=self._get_code_query_prompt_template(),
            input_variables=["context", "code_content", "user_query", "previous_response_context", "continuation_context", "response_type"]
        )
        
        return prompt_template | llm | StrOutputParser()

    def _get_code_query_prompt_template(self) -> str:
        """Returns the template for code query prompts"""
        return """You are an expert software developer and code analyst. 
        
        Guidelines:
        1. For general greetings or non-technical queries, respond briefly and naturally
        2. For technical questions:
            - Analyze the code thoroughly
            - Reference specific parts of the code when relevant
            - Provide code examples if needed
            - Acknowledge any uncertainties
            - Focus on the specific files and code provided
        3. Keep responses concise and relevant to the query's complexity
        4. If this is a continuation of a previous response, build upon it without repeating information
        
        Additional Context Information:
        {context}
        
        {previous_response_context}
        
        Code Files Content:
        {code_content}
        
        User Question: {user_query}
        
        {continuation_context}
        
        Please provide a{response_type} answer that matches the complexity and nature of the query:"""

    def prepare_query_context(self, previous_response: str, has_remaining_files: bool) -> Dict[str, str]:
        """Prepares context information for the code query"""
        previous_response_context = f"Previous partial response:\n{previous_response}" if previous_response else ""
        
        continuation_context = ""
        response_type = " complete"
        if has_remaining_files:
            continuation_context = (
                "NOTE: There are more files to analyze after this. "
                "Please provide a partial response based on the current files only. "
                "Your response will be combined with analysis of the remaining files."
            )
            response_type = " partial"
        
        return {
            "previous_response_context": previous_response_context,
            "continuation_context": continuation_context,
            "response_type": response_type
        }

    def _get_dependencies_analysis_prompt_template(self) -> str:
        """Returns the template for analyzing project dependencies and modules"""
        return """You are an expert software architect analyzing project dependencies and modules.

        Your task is to create a concise analysis focusing on reusable code components:

        1. Identify and extract code snippets that could be useful for future implementations
        2. For each relevant code section:
           - Extract the exact code snippet
           - Add a brief description of its purpose
           - Note any dependencies or requirements
        3. Focus only on code that could be directly reused or adapted
        4. Create a compact summary that can serve as a self-contained reference

        Guidelines:
        - Include complete, working code snippets that can be used without referring back to source files
        - Keep descriptions brief but clear
        - Include only the most relevant and reusable components
        - Format code snippets with proper markdown for easy extraction
        
        Additional Context Information:
        {context}
        
        Dependencies and Modules Content:
        {code_content}
        
        User Question: {user_query}
        
        {continuation_context}
        
        Please provide a{response_type} analysis in this format:
        1. Brief overview of found functionality (2-3 sentences max)
        2. Relevant code snippets formatted as:       ```language
           // Purpose: [brief description]
           // Dependencies: [if any]
           [exact code]       ```
        3. Quick reference of integration points (if applicable)"""

    def create_dependencies_analysis_chain(self, llm) -> RunnableSequence:
        """Creates a chain for analyzing project dependencies and modules"""
        prompt_template = PromptTemplate(
            template=self._get_dependencies_analysis_prompt_template(),
            input_variables=["context", "code_content", "user_query", "continuation_context", "response_type"]
        )
        
        return prompt_template | llm | StrOutputParser()

    def create_prompt_improver_chain(self, llm) -> RunnableSequence:
        """Creates a chain for improving user prompts with documentation context"""
        prompt_template = PromptTemplate(
            template="""You are an expert prompt engineer. Your task is to improve and restructure the user's query
            into a clear, concise prompt that will be used to generate code.

            Guidelines:
            1. Analyze both the user query and provided documentation
            2. Create a structured prompt that:
               - Maintains the original intent
               - Is more specific and detailed
               - Includes relevant technical context
               - Remains concise (no more than 2-3 sentences)
            3. DO NOT:
               - Add unnecessary complexity
               - Deviate from the original request
               - Make assumptions beyond the provided information

            Documentation Context:
            {documentation}

            Original User Query:
            {user_query}

            Please provide an improved prompt that is clear, specific, and ready for code generation:""",
            input_variables=["documentation", "user_query"]
        )
        
        return prompt_template | llm | StrOutputParser()

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
    