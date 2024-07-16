from typing import TypedDict, Annotated, List, Union

from langchain_core.agents import AgentAction, AgentFinish
import operator

class AgentState(TypedDict):
    input: str # accepts user's input as string
    agent_out : Union[AgentAction, AgentFinish, None] # gives output
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add] # shows intermediate steps


# In[2]:

with open("prompts/sample_data.txt", 'r') as file:
    data = file.read().strip()

import os.path
import logging
import sys

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai_api_key = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")


# In[5]:


# llama-index function
def llama_index(query: str):
    
    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
        documents = SimpleDirectoryReader("prompts").load_data()
        # By default, LlamaIndex uses a chunk size of 1024 and a chunk overlap of 20
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    
    query_engine = index.as_query_engine()
    # query_engine = index.as_query_engine(similarity_top_k=2, streaming=True) # to enable streaming
    # chat_engine = index.as_chat_engine() # to use chat engine for conversational search

    response = query_engine.query(query)
    # streaming_response = query_engine.query(query)
    # streaming_response.print_response_stream()
    # response = chat_engine.chat(query)
    return str(response)

# llama_index("what is immediate care?")
from langchain_core.tools import tool

@tool("search")
def search_tool(query: str):
    """Searches for information on the topic of providing immediate care."""
    # this is a "RAG" emulator
    # add RAG code
    answer = llama_index(query)
    return answer

@tool("final_answer")
def final_answer_tool(
    answer: str,
    source: str
):
    """Returns a natural language response to the user in `answer`, and a
    `source` from where this data is sourced from.
    """
    return ""


import os
from langchain.agents import create_openai_tools_agent
from langchain import hub
from langchain_openai import ChatOpenAI
# export LANGCHAIN_TRACING_V2="true"
# export LANGCHAIN_API_KEY="<key>"

# ALTERNATIVE PROMPT

from langchain.agents import create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.1
)

prompt_text = "You are an empathetic and supportive AI agent designed to provide interactive training and education to friends and family members of individuals dealing with mental health challenges. Your role is to equip them with the knowledge, skills, and confidence needed to offer effective mental health first aid and care to their loved ones.\n" \
              "Key Responsibilities:\n" \
              "- Engage in empathetic, personalized interactions that feel human-like and relatable\n" \
              "- Provide clear, accurate information about various mental health conditions and supportive strategies\n" \
              "- Guide users through interactive scenarios to build practical skills in a safe virtual environment\n" \
              "- Offer reassurance, validation and appreciation to users as they share their experiences and concerns\n" \
              "- Paraphrase user statements to confirm understanding, ending with validation checks (e.g. \"Did I understand that correctly?\")\n" \
              "- Ask clarifying questions to gather relevant context; do not make assumptions about the user's situation\n" \
              "- Tailor guidance to each user's unique circumstances, while reinforcing best practices in mental health first aid\n" \
              "- Maintain appropriate boundaries as an AI; direct users to professional help when needed\n" \
              "- Foster a non-judgmental, supportive tone that helps users feel heard and empowered to help their loved ones\n" \
              "Remember, your goal is to enhance understanding, improve communication skills, and ultimately enable users to create a more supportive environment for those struggling with mental health issues. Approach each interaction with compassion, respect for individual experiences, and a commitment to providing reliable, constructive guidance. Together, we can make a meaningful difference in the lives of individuals and families navigating mental health challenges."

prompt = ChatPromptTemplate.from_messages([
  ("system", prompt_text),
  ("placeholder", "{chat_history}"),
  ("human", "{input}"),
  ("placeholder", "{agent_scratchpad}"),
])

planner_agent_runnable = create_openai_tools_agent(
    llm=llm,
    tools=[final_answer_tool, search_tool],
    prompt=prompt
)

# ### Define Nodes for Graph

from langchain_core.agents import AgentFinish
import json

def run_planner_agent(state: list):
    print("> run_planner_agent")
    agent_out = planner_agent_runnable.invoke(state)
    return {"agent_out": agent_out}

def execute_search(state: list):
    print("> execute_search")
    action = state["agent_out"]
    tool_call = action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]
    out = search_tool.invoke(
        json.loads(tool_call["function"]["arguments"])
    )
    return {"intermediate_steps": [{"search": str(out)}]}

def router(state: list):
    print("> router")
    if isinstance(state["agent_out"], list) and state["agent_out"]:
        return state["agent_out"][-1].tool
    else:
        return "error"

# finally, we will have a single LLM call that MUST use the final_answer structure
final_answer_llm = llm.bind_tools([final_answer_tool], tool_choice="final_answer")

# this forced final_answer LLM call will be used to structure output from our
# RAG endpoint
def rag_final_answer(state: list):
    print("> final_answer")
    query = state["input"]
    context = state["intermediate_steps"][-1]

    prompt = f"""You are a helpful assistant, answer the user's question using the
    context provided.

    CONTEXT: {context}

    QUESTION: {query}
    """
    out = final_answer_llm.invoke(prompt)
    function_call = out.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
    return {"agent_out": function_call}

# we use the same forced final_answer LLM call to handle incorrectly formatted
# output from our planner_agent
def handle_error(state: list):
    print("> handle_error")
    query = state["input"]
    prompt = f"""You are a helpful assistant, answer the user's question.

    QUESTION: {query}
    """
    out = final_answer_llm.invoke(prompt)
    function_call = out.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
    return {"agent_out": function_call}
