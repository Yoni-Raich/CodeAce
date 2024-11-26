from mapping_agent import MappingAgent 
# from core_agent import CoreAgent
src = r"C:\CodeAce\managers"

mapping_agent = MappingAgent(model_name="azure", src_path=src)
mapping_agent.run_mapping_process()
# core_agent = CoreAgent(model_name="azure", src_path=src)
