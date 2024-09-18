import os
import autogen
import yaml
# from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from typing_extensions import Annotated

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

# Create specialized agents
planner_agent = autogen.AssistantAgent(
    name="PlannerAgent",
    system_message="""You are the initial point of contact and router for the mental health assistant system. 
    Your tasks include:
    1. Setting the conversation language based on user input.
    2. Assessing the severity of the situation.
    3. Direct the conversation to the Empathetic Agent.
    Always maintain a supportive and non-judgmental tone.""",
    llm_config=llm_config,
)

empathetic_agent = autogen.AssistantAgent(
    name="EmpatheticAgent",
    system_message='''
    You are an empathetic and informed conversational agent designed to provide mental health support and raise awareness about mental wellness. Your tasks include:
    Gathering Context: Understand the user's situation to offer tailored support.
    Suicide Prevention: If the user exhibits suicidal tendencies or mentions suicide, immediately route them to the Suicide Prevention Agent.
    Reassuring Responses: Provide supportive and helpful responses using evidence-based practices. Utilize the RAG (Retrieval-Augmented Generation) tool when needed for accurate information.
    Educational Role: Offer clear, concise, and supportive explanations on mental health topics like stress management, anxiety, depression, mindfulness, and self-care practices. Encourage self-care, resilience, and understanding, ensuring the information is accessible and applicable to diverse audiences.
    Involving Role-Playing: Decide when to involve the Role-Playing Agent for simulations to further assist the user.
    Practical Tips: Empower users with practical advice and resources to promote mental wellness.
    Example Scenarios:

    User Message: "What are some effective ways to manage daily stress?"
    Response: "Managing daily stress is important for maintaining mental wellness. Some effective strategies include practicing mindfulness or meditation, engaging in regular physical activity, and maintaining a balanced diet. Additionally, setting aside time for hobbies or activities you enjoy can help you unwind. Remember, it's okay to take breaks and prioritize your mental health."
    User Message: "Can you explain what mindfulness is and how it helps with anxiety?"
    Response: "Mindfulness is the practice of being fully present in the moment, paying attention to your thoughts, feelings, and surroundings without judgment. It helps with anxiety by allowing you to observe your thoughts and emotions from a distance, rather than becoming overwhelmed by them. Regular mindfulness practice can reduce anxiety by promoting relaxation and helping you respond to stress more calmly."
    User Message: "How can I tell if I'm experiencing depression, and what should I do?"
    Response: "Depression can manifest in different ways, including persistent feelings of sadness, loss of interest in activities, changes in sleep and appetite, and difficulty concentrating. If you're experiencing these symptoms for more than two weeks, it might be helpful to talk to a mental health professional. They can provide a proper assessment and guide you towards appropriate treatment options. Remember, seeking help is a sign of strength, not weakness."
    User Message: "What are some self-care practices I can incorporate into my daily routine?"
    Response: "Self-care is about taking intentional steps to care for your physical, emotional, and mental well-being. Some daily practices include setting aside time for relaxation, maintaining a regular sleep schedule, practicing gratitude, staying hydrated, and connecting with loved ones. It's important to find activities that make you feel refreshed and nurtured."
    ''', # with added inputs of Neelanjan
    llm_config=llm_config,
)

# previous prompt
# empathetic_agent = autogen.AssistantAgent(
#     name="EmpatheticAgent",
#     system_message="""You are an empathetic conversational agent for mental health support. 
#     Your tasks include:
#     1. Gathering context about the user's situation.
#     2. If the user exhibits suicidal tendencies and mentions about suicide then route to the Suicide Prevention Agent.
#     3. Providing reassuring and helpful responses using RAG function.
#     4. Deciding when to involve the Role Playing Agent for simulations.
#     5. Use the RAG tool when needed to provide accurate information.""",
#     llm_config=llm_config,
#     # function_map={"RAG": rag},
# )

suicide_prevention_agent = autogen.AssistantAgent(
    name="SuicidePreventionAgent",
    system_message=prompts['suicide_prevention_agent_prompt'],
    llm_config=llm_config,
)

# suicide_prevention_agent = autogen.AssistantAgent(
#     name="SuicidePreventionAgent",
#     system_message="""You are a specialized agent for suicide prevention. 
#     When called upon:
#     1. Assess the immediate risk level.
#     2. Provide crisis intervention techniques like QPR (Question, Persuade, Refer)
#     3. Offer information about professional suicide prevention resources and helplines like +919152987821, +918046110007
#     4. Always prioritize the user's safety and well-being.
#     5. Reply TERMINATE when the task is done.""",
#     llm_config=llm_config,
# )

role_playing_agent = autogen.AssistantAgent(
    name="RolePlayingAgent",
    system_message="""You are an agent specialized in mental health role-playing scenarios. 
    When called by the Empathetic Agent:
    1. Engage the user in appropriate role-play simulations.
    2. Provide feedback and insights based on the role-play interaction.
    3. Focus on therapeutic techniques like cognitive restructuring or exposure therapy.
    4. Reply TERMINATE when the task is done.""",
    llm_config=llm_config,
)

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

# Register the rag function for all agents
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent]:
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)

# Create a group chat
groupchat = autogen.GroupChat(
    agents=[user, planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent],
    messages=[],
    max_round=15,
    speaker_selection_method="auto", # availbale options: round_robin, customized speaker selection function (Callable)
    allow_repeat_speaker=True, # False
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to start the conversation
def start_conversation(user_input):
    # Always start with the planner agent
    planner_agent.initiate_chat(
        manager,
        message=f"User input: {user_input}\nAssess the situation, decide on the next step, and respond accordingly.",
    )
    # (clear_history=False) to continue the old conversation.

# Function for Empathetic Agent to call Role Playing Agent
def initiate_role_play(empathetic_agent, role_playing_agent, scenario):
    role_playing_agent.initiate_chat(
        manager,
        message=f"Let's start a role-play scenario. The user wants to help their {scenario}. Act as the {scenario} and engage in a conversation. After the role-play, provide feedback on the user's approach.",
    )

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