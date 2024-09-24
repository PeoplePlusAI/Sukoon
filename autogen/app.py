# checkout to autogen branch

import os
import autogen
import yaml

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

# from autogen import ConversableAgent
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

# Create a user proxy agent
user = autogen.UserProxyAgent(
    name="User",
    is_termination_msg=termination_msg,
    human_input_mode="ALWAYS", # "NEVER", "TERMINATE"
    max_consecutive_auto_reply=3,
    code_execution_config={"use_docker": False}, # "work_dir":"_output"
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    # function_map={"ask_expert": ask_expert},
)

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

planner_agent = autogen.AssistantAgent(
    name="PlannerAgent",
    system_message=prompts['planner_agent_prompt'],
    llm_config=llm_config,
)

empathetic_agent = autogen.AssistantAgent(
    name="EmpatheticAgent",
    system_message=prompts['empathetic_agent_prompt'],
    llm_config=llm_config,
)

suicide_prevention_agent = autogen.AssistantAgent(
    name="SuicidePreventionAgent",
    system_message=prompts['suicide_prevention_agent_prompt'],
    llm_config=llm_config,
)

# role_playing_agent = autogen.AssistantAgent(
#     name="RolePlayingAgent",
#     system_message=prompts['role_playing_agent_prompt'],
#     llm_config=llm_config,
# )

# Register the rag function for all agents
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent]: #role_playing_agent
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)

# Create a group chat
groupchat = autogen.GroupChat(
    agents=[user, planner_agent, empathetic_agent, suicide_prevention_agent], #role_playing_agent
    messages=[],
    max_round=10,
    speaker_selection_method="auto", # availbale options: round_robin, customized speaker selection function (Callable)
    allow_repeat_speaker=True, # False
    # allowed_or_disallowed_speaker_transitions={
    #     user: [planner_agent, empathetic_agent, suicide_prevention_agent],
    #     planner_agent: [user, empathetic_agent, suicide_prevention_agent],
    #     empathetic_agent: [user, suicide_prevention_agent],
    #     suicide_prevention_agent: [user, planner_agent],
    #     role_playing_agent: [user, empathetic_agent, suicide_prevention_agent],
    # },
    # speaker_transitions_type="allowed",
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to start the conversation
def start_conversation(user_input):
    # Always start with the planner agent
    planner_agent.initiate_chat(
        manager,
        message=f"User input: {user_input}\nAssess the situation, decide on the next step, and respond accordingly.",
    )

# Function for Empathetic Agent to call Role Playing Agent
# def initiate_role_play(empathetic_agent, role_playing_agent, scenario):
#     role_playing_agent.initiate_chat(
#         manager,
#         message=f"Let's start a role-play scenario. The user wants to help their {scenario}. Act as the {scenario} and engage in a conversation. After the role-play, provide feedback on the user's approach.",
#     )

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
        print()
        start_conversation(user_input)
        print()
        
        
# # to check all message summary history
# from autogen import initiate_chats
# # chats = [{list of tasks}]
# chat_results = initiate_chats(chats)

# for chat_result in chat_results:
#     print(chat_result.summary)

# # to measure costs 
# for chat_result in chat_results:
#     print(chat_result.cost)
#     print("\n")