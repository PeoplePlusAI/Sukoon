import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from typing_extensions import Annotated

# Configure the agents
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.7}

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

# Create a user proxy agent
user = autogen.UserProxyAgent(
    name="User",
    is_termination_msg=termination_msg,
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=3,
    code_execution_config=False,  # Disable code execution
)

# Create a RAG agent for data retrieval
rag_agent = RetrieveUserProxyAgent(
    name="MentalHealthKnowledgeBase",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "qa",
        "docs_path": "path/to/your/mental_health_docs",  # Replace with actual path
        "chunk_token_size": 1000,
        "model": config_list[0]["model"],
        "client": "openai",
        "embedding_model": "text-embedding-ada-002",
        "get_or_create": True,
    },
    code_execution_config=False,  # Disable code execution
)

# Create specialized assistant agents
therapist = autogen.AssistantAgent(
    name="Therapist",
    system_message="""You are an AI therapist with expertise in mental health counseling. 
    Provide empathetic and supportive responses based on established therapeutic techniques. 
    Always encourage seeking professional help for serious concerns.""",
    llm_config=llm_config,
)

psychiatrist = autogen.AssistantAgent(
    name="Psychiatrist",
    system_message="""You are an AI psychiatrist with expertise in mental health diagnoses and treatments. 
    Provide information about mental health conditions and general treatment approaches. 
    Never prescribe medication or provide specific medical advice.""",
    llm_config=llm_config,
)

wellness_coach = autogen.AssistantAgent(
    name="WellnessCoach",
    system_message="""You are an AI wellness coach focusing on mental health and well-being. 
    Provide practical advice on lifestyle changes, stress management, and self-care techniques 
    to improve overall mental health.""",
    llm_config=llm_config,
)

# Function to retrieve content using the RAG agent
def retrieve_content(
    message: Annotated[str, "Message to retrieve content for"],
    n_results: Annotated[int, "Number of results"] = 3
) -> str:
    rag_agent.n_results = n_results
    update_context_case1, update_context_case2 = rag_agent._check_update_context(message)
    if (update_context_case1 or update_context_case2) and rag_agent.update_context:
        rag_agent.problem = message if not hasattr(rag_agent, "problem") else rag_agent.problem
        _, ret_msg = rag_agent._generate_retrieve_user_reply(message)
    else:
        _context = {"problem": message, "n_results": n_results}
        ret_msg = rag_agent.message_generator(rag_agent, None, _context)
    return ret_msg if ret_msg else message

# Register the retrieve_content function for all agents
for agent in [therapist, psychiatrist, wellness_coach]:
    agent.register_for_llm(
        description="Retrieve content related to mental health topics.",
        api_style="function"
    )(retrieve_content)

user.register_for_execution()(retrieve_content)

# Create a group chat
groupchat = autogen.GroupChat(
    agents=[user, therapist, psychiatrist, wellness_coach],
    messages=[],
    max_round=15,
    speaker_selection_method="round_robin",
    allow_repeat_speaker=False,
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to start the conversation
def start_conversation(user_input):
    user.initiate_chat(
        manager,
        message=user_input,
    )

# Main loop
if __name__ == "__main__":
    print("Welcome to the Enhanced Mental Health Assistant.")
    print("You can discuss your concerns with our team of AI specialists.")
    print("Type 'quit' to exit the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Thank you for using the Mental Health Assistant. Take care!")
            break
        start_conversation(user_input)