from codeace import MappingAgent, CoreAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define source paths
src_path = r"path/to/main/codebase/src"  # Main codebase path
modules_src = r"path/to/modules/src"      # Modules/dependencies path

# Initialize agents
mapping_agent = MappingAgent(model_name="azure", src_path=src_path)
mapping_agent.run_mapping_process()  # Map the main codebase

# Initialize core agents for different parts of the codebase
main_agent = CoreAgent(model_name="azure", src_path=src_path)
modules_agent = CoreAgent(model_name="azure", src_path=modules_src)

# Add documentation context
main_agent.add_extra_context_by_path("path/to/documentation.md")

# Interactive query loop
user_prompt = input("Enter your query (type 'exit' to quit): ")
while user_prompt != "exit":
    # Improve the user prompt using documentation context
    improved_prompt = main_agent.improve_user_prompt(user_prompt)
    
    # First, analyze dependencies in modules
    dependencies_files = modules_agent.find_relevant_files(user_prompt)
    dependencies_result = modules_agent.process_dependencies_query(user_prompt, dependencies_files)
    print("\nDependencies Analysis:")
    print(dependencies_result)
    
    # Add dependencies context to main analysis
    main_agent.add_extra_context(dependencies_result)
    
    # Process main codebase query
    relevant_files = main_agent.find_relevant_files(user_prompt)
    result = main_agent.process_code_query(user_prompt, relevant_files)
    print("\nMain Analysis:")
    print(result)
    
    user_prompt = input("\nEnter your query (type 'exit' to quit): ")