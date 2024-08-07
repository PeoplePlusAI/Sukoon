import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

# Configure the agents
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

# Create a RAG agent for data retrieval
rag_agent = RetrieveUserProxyAgent(
    name="rag_agent",
    system_message="You are a retrieval agent. Your role is to fetch relevant information from the knowledge base to support the doctor's responses.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "qa",
        "docs_path": "data/sample_data.txt", # /../data/sample_data.txt
        "chunk_token_size": 1000,
        "model": config_list[0]["model"],
        "client": "openai",
        "embedding_model": "text-embedding-ada-002",
        "get_or_create": True,
    },
)

# Create a doctor-like assistant agent
doctor_assistant = GPTAssistantAgent(
    name="doctor_assistant",
    llm_config={
        "config_list": config_list,
        "assistant_id": "YOUR_ASSISTANT_ID",  # Replace with your actual Assistant ID
    },
    system_message="""You are an AI assistant with expertise in mental health, 
    thinking and responding like a compassionate and knowledgeable doctor. 
    Provide supportive advice and information about mental health topics based on the context provided by the RAG agent. 
    Remember to always encourage users to seek professional help for serious concerns. 
    Never provide diagnoses or medical advice that should come from a licensed professional.""",
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

# Create a group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, rag_agent, doctor_assistant],
    messages=[],
    max_round=15,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config={
        "config_list": config_list,
    },
)

# Function to start the conversation
def start_conversation(user_input):
    user_proxy.initiate_chat(
        manager,
        message=user_input,
    )

# Main loop
if __name__ == "__main__":
    print("Welcome to the Mental Health Advice Chat with RAG support.")
    print("Please share your concerns or ask questions about mental health.")
    print("Type 'quit' to exit the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Thank you for using the Mental Health Advice Chat. Take care!")
            break
        start_conversation(user_input)