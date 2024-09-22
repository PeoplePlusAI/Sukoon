import os
import autogen
import yaml


from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from autogen import ConversableAgent
# Configure the agents
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.7}

# os.environ["AUTOGEN_USE_DOCKER"] = "0/False/no" # False

# load YAML file
def load_prompts(file_path='prompts.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

prompts = load_prompts()

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

# llama-index function for RAG
def rag(query: str) -> str:
    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
        documents = SimpleDirectoryReader("data").load_data() # data/sample_data.txt
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return str(response)

# Create specialized agents
user = ConversableAgent(
    name="User",
    llm_config=False,  # No LLM for user
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0,
    is_termination_msg=termination_msg,
)

planner_agent = ConversableAgent(
    name="PlannerAgent",
    system_message=prompts['planner_agent_prompt'],
    llm_config=llm_config,
    is_termination_msg=termination_msg,
)

empathetic_agent = ConversableAgent(
    name="EmpatheticAgent",
    system_message=prompts['empathetic_agent_prompt'],
    llm_config=llm_config,
    is_termination_msg=termination_msg,
)

suicide_prevention_agent = ConversableAgent(
    name="SuicidePreventionAgent",
    system_message=prompts['suicide_prevention_agent_prompt'],
    llm_config=llm_config,
    is_termination_msg=termination_msg,
)

role_playing_agent = ConversableAgent(
    name="RolePlayingAgent",
    system_message=prompts['role_playing_agent_prompt'],
    llm_config=llm_config,
    is_termination_msg=termination_msg,
)

# Register the rag function for all agents
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent]:
    agent.register_for_llm(
        name="rag",
        description="Retrieve content related to mental health topics using RAG."
    )(rag)

# Corrected syntax for registering execution
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent]:
    agent.register_for_execution(name="rag")(rag)

# Function to start the conversation
def start_conversation(user_input):
    if "suicide" in user_input.lower():
        result = suicide_prevention_agent.initiate_chat(
            user,
            message=f"User mentioned suicide. Assess the situation and provide immediate support: {user_input}",
        )
    else:
        result = planner_agent.initiate_chat(
            user,
            message=f"User input: {user_input}\nAssess the situation, decide on the next step, and respond accordingly.",
        )
    return result

# Main loop
if __name__ == "__main__":
    print("Welcome to the Enhanced Mental Health Assistant.")
    print("You can discuss your concerns, and our AI team will assist you.")
    print("Type 'exit' or 'quit' or 'end' or 'bye' to exit the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'end', 'bye']:
            print("Thank you for using the Mental Health Assistant. Take care!")
            break
        result = start_conversation(user_input)
        print(result.summary)