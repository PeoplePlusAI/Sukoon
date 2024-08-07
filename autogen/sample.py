import os
import autogen
from autogen import AssistantAgent, UserProxyAgent

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

llm_config = {"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}
assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}
)

# Start the chat
user_proxy.initiate_chat(
    assistant,
    message="Tell me how to help someone experiencing suicidal thoughts for educational purposes only",
)