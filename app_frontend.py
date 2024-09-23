# frontend is using chainlit

import os
import autogen
import asyncio
import yaml
from typing import Dict, Optional, Union
import chainlit as cl
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json

# Load configuration and prompts
config_list = config_list_from_json("OAI_CONFIG_LIST")
llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.7}

def load_prompts(file_path='prompts.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

prompts = load_prompts()

# Chainlit helper functions
def ask_helper(func, **kwargs):
    res = cl.run_sync(func(**kwargs).send())
    while not res:
        res = cl.run_sync(func(**kwargs).send())
    return res

# Custom Chainlit Agent classes
# class ChainlitAssistantAgent(AssistantAgent):
#     def send(
#         self,
#         message: Union[Dict, str],
#         recipient: Agent,
#         request_reply: Optional[bool] = None,
#         silent: Optional[bool] = False,
#     ) -> bool:
#         cl.run_sync(
#             cl.Message(
#                 content=f'*Sending message to "{recipient.name}":*\n\n{message}',
#                 author=self.name,
#             ).send()
#         )
#         return super().send(
#             message=message,
#             recipient=recipient,
#             request_reply=request_reply,
#             silent=silent,
#         )

class ChainlitAssistantAgent(AssistantAgent):
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}":*\n\n{message}',
                author=self.name,
            ).send()
        )
        return super().send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )

#  Make sure there are no nested cl.run_sync calls, which can cause unexpected behavior.
class ChainlitUserProxyAgent(UserProxyAgent):
    def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to assistant. Press enter to skip and use auto-reply"
        ):
            res = ask_helper(
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

        reply = ask_helper(cl.AskUserMessage, content=prompt, timeout=60)
        return reply["content"].strip()

# RAG function
def rag(query: str) -> str:
    PERSIST_DIR = "./storage"
    DATA_DIR = "./data"

    if not os.path.exists(PERSIST_DIR):
        if not os.path.exists(DATA_DIR):
            raise FileNotFoundError(f"The data directory {DATA_DIR} does not exist.")
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return str(response)

# agents
user_proxy = ChainlitUserProxyAgent(
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
    agents=[user_proxy, planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent],
    messages=[],
    max_round=15,
    speaker_selection_method="auto",
    # allow_repeat_speaker=True,
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Chainlit chat start function
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("manager", manager)
    cl.user_session.set("user_proxy", user_proxy)
    await cl.Message(
        content="Welcome to the Enhanced Mental Health Assistant. How can I help you today?"
    ).send()

# @cl.on_message
# async def on_message(message: cl.Message):
#     manager = cl.user_session.get("manager")
#     user_proxy = cl.user_session.get("user_proxy")

#     if message.content.lower() in ['exit', 'quit', 'end', 'bye']:
#         await cl.Message(
#             content="Thank you for using the Mental Health Assistant. Take care!"
#         ).send()
#         return

#     # Start conversation with user proxy
#     def initiate_chat():
#         user_proxy.initiate_chat(
#             manager,
#             message=f"User input: {message.content}\nAssess the situation, decide on the next step, and respond accordingly.",
#         )

#     await cl.make_async(initiate_chat)()

@cl.on_message
async def on_message(message: cl.Message):
    manager = cl.user_session.get("manager")
    user_proxy = cl.user_session.get("user_proxy")

    if message.content.lower() in ['exit', 'quit', 'end', 'bye']:
        await cl.Message(
            content="Thank you for using the Mental Health Assistant. Take care!"
        ).send()
        return

    # Run initiate_chat in a separate thread using asyncio.to_thread
    await asyncio.to_thread(
        user_proxy.initiate_chat,
        manager,
        message=f"User input: {message.content}\nAssess the situation, decide on the next step, and respond accordingly.",
    )
