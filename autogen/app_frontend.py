import os
import autogen
import yaml
from typing import Dict, Optional, Union
from typing_extensions import Annotated
import chainlit as cl
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

# Load configuration and prompts
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.7}

def load_prompts(file_path='prompts.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

prompts = load_prompts()

# Chainlit helper functions
async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

# Custom Chainlit Agent classes
class ChainlitAssistantAgent(autogen.AssistantAgent):
    async def send(self, message: Union[Dict, str], recipient: autogen.Agent, request_reply: Optional[bool] = None, silent: Optional[bool] = False):
        await cl.Message(content=f'*Sending message to "{recipient.name}":*\n\n{message}', author=self.name).send()
        super().send(message=message, recipient=recipient, request_reply=request_reply, silent=silent)

class ChainlitUserProxyAgent(autogen.UserProxyAgent):
    async def get_human_input(self, prompt: str) -> str:
        if prompt.startswith("Provide feedback to assistant. Press enter to skip and use auto-reply"):
            res = await ask_helper(
                cl.AskActionMessage,
                content="Continue or provide feedback?",
                actions=[
                    cl.Action(name="continue", value="continue", label="✅ Continue"),
                    cl.Action(name="feedback", value="feedback", label="💬 Provide feedback"),
                    cl.Action(name="exit", value="exit", label="🔚 Exit Conversation"),
                ],
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "exit"
        reply = await ask_helper(cl.AskUserMessage, content=prompt, timeout=60)
        return reply["content"].strip()

    async def send(self, message: Union[Dict, str], recipient: autogen.Agent, request_reply: Optional[bool] = None, silent: Optional[bool] = False):
        await cl.Message(content=f'*Sending message to "{recipient.name}"*:\n\n{message}', author=self.name).send()
        super().send(message=message, recipient=recipient, request_reply=request_reply, silent=silent)

# RAG function
def rag(query: str) -> str:
    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return str(response)

# Create agents
user = ChainlitUserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=3,
    code_execution_config={"use_docker": False},
)

planner_agent = ChainlitAssistantAgent(
    name="PlannerAgent",
    system_message=prompts['planner_agent_prompt'],
    llm_config=llm_config,
)

empathetic_agent = ChainlitAssistantAgent(
    name="EmpatheticAgent",
    system_message=prompts['empathetic_agent_prompt'],
    llm_config=llm_config,
)

suicide_prevention_agent = ChainlitAssistantAgent(
    name="SuicidePreventionAgent",
    system_message=prompts['suicide_prevention_agent_prompt'],
    llm_config=llm_config,
)

role_playing_agent = ChainlitAssistantAgent(
    name="RolePlayingAgent",
    system_message=prompts['role_playing_agent_prompt'],
    llm_config=llm_config,
)

# Register RAG function for all agents
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent]:
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)

# Create group chat
groupchat = autogen.GroupChat(
    agents=[user, planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent],
    messages=[],
    max_round=15,
    speaker_selection_method="auto",
    allow_repeat_speaker=True,
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Chainlit chat start function
@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Welcome to the Enhanced Mental Health Assistant. How can I help you today?").send()

# Chainlit message handler
@cl.on_message
async def on_message(message: str):
    if message in ['exit', 'quit', 'end', 'bye']:
        await cl.Message(content="Thank you for using the Mental Health Assistant. Take care!").send()
        return

    # Start conversation with planner agent
    response = await cl.make_async(planner_agent.initiate_chat)(
        manager,
        message=f"User input: {message}\nAssess the situation, decide on the next step, and respond accordingly.",
    )

    # Process and send the response
    if isinstance(response, str):
        await cl.Message(content=response).send()
    elif isinstance(response, dict) and 'content' in response:
        await cl.Message(content=response['content']).send()
    else:
        await cl.Message(content="I'm sorry, I couldn't process that response. Can you please try again?").send()