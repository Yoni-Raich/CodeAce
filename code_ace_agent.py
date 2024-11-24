import json
from managers.llm_manager import LLMManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class MappingFile(BaseModel):
    fileName: str = Field(description="full path and name of the file")
    description: str = Field(description="description of the file content")    

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

# Agent functionality
#agent = CodeAce("llm name", "src_path", "AppData_path")
#agent.mapping_process()

# 1. agent.set_prompt("prompt")
# 2. rl_file = agent.search_relevet_files()
# 3. res = agent.invoke(rl_file)

