import os
import autogen
import yaml

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

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

# # Create a RAG agent for data retrieval
# rag_tool = RetrieveUserProxyAgent(
#     name="MentalHealthKnowledgeBase",
#     is_termination_msg=termination_msg,
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=3,
#     retrieve_config={
#         "task": "qa",
#         "docs_path": "data/sample_data.txt",  # Replace with actual path
#         "chunk_token_size": 200,
#         "model": config_list[0]["model"],
#         "client": "openai",
#         "embedding_model": "text-embedding-ada-003",
#         "get_or_create": True,
#     },
#     # code_execution_config={"use_docker": False},
# )

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

agents = {
    "planner": autogen.AssistantAgent(
        name="PlannerAgent",
        system_message=prompts['planner_agent_prompt'],
        llm_config=llm_config,
    ),
    "empathetic": autogen.AssistantAgent(
        name="EmpatheticAgent",
        system_message=prompts['empathetic_agent_prompt'],
        llm_config=llm_config,
    ),
    "suicide_prevention": autogen.AssistantAgent(
        name="SuicidePreventionAgent",
        system_message=prompts['suicide_prevention_agent_prompt'],
        llm_config=llm_config,
    )
}

for agent in agents.values():
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)

groupchat = autogen.GroupChat(
    agents=[user, agents["empathetic"], agents["suicide_prevention"]], ##role_playing_agent
    messages=[],
    max_round=15,
    speaker_selection_method="auto", # availbale options: round_robin, customized speaker selection function (Callable)
    allow_repeat_speaker=True, # False
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to start the conversation
def start_conversation(user_input):
    agents["planner"].initiate_chat(
        manager,
        message=f"User input: {user_input}\nAssess the situation, decide on the next step, and respond accordingly.",
    )
    # (clear_history=False) to continue the old conversation.

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
        start_conversation(user_input)
        

# # Function to retrieve content using the RAG tool
# def retrieve_content(
#     message: Annotated[str, "Message to retrieve content for"],
#     n_results: Annotated[int, "Number of results"] = 3
# ) -> str:
#     rag_tool.n_results = n_results
#     update_context_case1, update_context_case2 = rag_tool._check_update_context(message)
#     if (update_context_case1 or update_context_case2) and rag_tool.update_context:
#         rag_tool.problem = message if not hasattr(rag_tool, "problem") else rag_tool.problem
#         _, ret_msg = rag_tool._generate_retrieve_user_reply(message)
#     else:
#         _context = {"problem": message, "n_results": n_results}
#         ret_msg = rag_tool.message_generator(rag_tool, None, _context)
#     return ret_msg if ret_msg else message
