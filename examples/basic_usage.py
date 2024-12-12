from codeace import MappingAgent, CoreAgent
src = r"\\10.12.231.83\c\Users\Administrator\Documents\repositories\Temp\MfgTools\src"

mapping_agent = MappingAgent(model_name="azure", src_path=src)
#mapping_agent.run_mapping_process()
core_agent = CoreAgent(model_name="azure", src_path=src)

moduls_src = "\\\\10.12.231.83\\c\\Users\\Administrator\\Documents\\repositories\\New-MfgTools\\Modules\\src\\ManufacturingToolsModules"
pre_agent = CoreAgent(model_name="azure", src_path=moduls_src)

user_prompt = input("Enter your query: ")
while user_prompt != "exit":
    core_agent.add_extra_context_by_path(r"C:\streamlit_gui\LineTools_documentation.md")
    improved_prompt = core_agent.improve_user_prompt(user_prompt)
    
    dependencies_relevant_files = pre_agent.find_relevant_files(user_prompt)
    dependencies_result = pre_agent.process_dependencies_query(user_prompt, dependencies_relevant_files)
    print("\n\n")
    print(dependencies_result)
    print("\n\n")
    core_agent.add_extra_context_by_path()
    core_agent.add_extra_context(dependencies_result)

    relevant_files = core_agent.find_relevant_files(user_prompt)
    result = core_agent.process_code_query(user_prompt, relevant_files)
    
    user_prompt = input("Enter your query: ")