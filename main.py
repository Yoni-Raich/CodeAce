from mapping_agent import MappingAgent
from core_agent import CoreAgent
src = r"C:\CodeAce\managers"

mapping_agent = MappingAgent(model_name="azure", src_path=src)
mapping_agent.run_mapping_process()
core_agent = CoreAgent(model_name="azure", src_path=src)

user_prompt = input("Enter your query: ")
while user_prompt != "exit":
    relevant_files = core_agent.find_relevant_files(user_prompt)
    print(f'found {len(relevant_files)} relevant files')
    result = core_agent.process_code_query(user_prompt, relevant_files)
    print(result)
    user_prompt = input("Enter your query: ")