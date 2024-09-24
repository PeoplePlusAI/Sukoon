# please checkout to langgraph branch

from openai import OpenAI
from typing import TypedDict, Annotated, List, Union

from langchain_core.agents import AgentAction, AgentFinish
import operator

import os.path
import logging
import sys
import re

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

class AgentState(TypedDict):
    input: str # accepts user's input as string
    agent_out : Union[AgentAction, AgentFinish, None] # gives output
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add] # shows intermediate steps

with open("prompts/sample_data.txt", 'r') as file:
    data = file.read().strip()

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

# Caching mechanism for search results
# @lru_cache(maxsize=100)
# def cached_search(query: str):
#     # Implement actual search logic here
#     return f"Cached search result for: {query}"

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

### Role playing part
@tool("role_play")
def role_play_tool(query: str):
    """Performs a role-play scenario for mental health first aid using AI."""
    return chat_completion(query)


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
    model="gpt-4o", # compare mini and gpt4o , see the most important this is eval. so have one loop scenario to test this and eval if loop is fine .. do this first before fixing any framework like langgraph .. i use autogen. but
    # if u have already done this langgraph.. dont do everything at first. just plan one convo scenario first. eval if it is doing well. 
    # so for eg lets do the scenario in board.
    openai_api_key=openai_api_key,
    temperature=0.1
)

prompt_text = "You are an empathetic and supportive AI agent designed to provide interactive training and education to friends and family members of individuals dealing with mental health challenges. Your role is to equip them with the knowledge, skills, and confidence needed to offer effective mental health first aid and care to their loved ones.\n" \
              "Key Responsibilities:\n" \
              "- Engage in empathetic, personalized interactions that feel human-like and relatable\n" \
              "- Provide clear, accurate information about various mental health conditions and supportive strategies\n" \
              "- Guide users through interactive scenarios to build practical skills in a safe virtual environment. You may engage in role play to achieve this like showing a conversation between a father trying to help her distressed daughter \n" \
              "- Offer reassurance, validation and appreciation to users as they share their experiences and concerns\n" \
              "- Paraphrase user statements to confirm understanding, ending with validation checks (e.g. \"Did I understand that correctly?\")\n" \
              "- Ask clarifying questions to gather relevant context; do not make assumptions about the user's situation\n" \
              "- Tailor guidance to each user's unique circumstances, while reinforcing best practices in mental health first aid\n" \
              "- Foster a non-judgmental, supportive tone that helps users feel heard and empowered to help their loved ones\n" \
              "Remember, your goal is to enhance understanding, improve communication skills, and ultimately enable users to create a more supportive environment for those struggling with mental health issues. Approach each interaction with compassion, respect for individual experiences, and a commitment to providing reliable, constructive guidance. Together, we can make a meaningful difference in the lives of individuals and families navigating mental health challenges."
# Output without any formatting, using just 2 emojis. Output in bullet numbering format

prompt = ChatPromptTemplate.from_messages([
  ("system", prompt_text),
  ("placeholder", "{chat_history}"),
  ("human", "{input}"),
  ("placeholder", "{agent_scratchpad}"),
])


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

def execute_role_play(state: list):
    print("> execute_role_play")
    action = state["agent_out"]
    tool_call = action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]
    out = role_play_tool.invoke(
        json.loads(tool_call["function"]["arguments"])
    )
    return {"intermediate_steps": [{"role_play": str(out)}]}

# for role playing
# use AI assistant for interactive chat
def chat_completion(query):
    client = OpenAI(api_key=openai_api_key)
    prompt_text = """You are an empathetic AI trained to perform role-play scenarios for mental health first aid. Given a situation, you will output a constructive dialogue showing how to provide effective support. Your responses should be compassionate, informative, and tailored to the specific scenario. For example, if asked about helping a daughter feeling suicidal, you'll demonstrate a supportive conversation between a parent and child, emphasizing active listening, validation of feelings, and appropriate steps for seeking professional help."""

    response = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4 for more nuanced responses
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": query}
        ],
        temperature=0.7  # Slightly increased for more creative responses
    )
    return response.choices[0].message.content

planner_agent_runnable = create_openai_tools_agent(
    llm=llm,
    tools=[final_answer_tool, search_tool, role_play_tool],
    prompt=prompt
)

def router(state: dict):
    print("> router")
    input_text = state["input"].lower()
    
    # Keywords that might indicate a need for role play
    role_play_keywords = [
        "role play", "scenario", "simulate", "practice", "conversation",
        "dialogue", "interact", "pretend", "act out", "example situation"
    ]
    
    # Keywords that indicate a request for mental health first aid information
    mhfa_keywords = [
        "mental health first aid", "mhfa", "first aid for mental health",
        "mental health support", "mental health assistance",
        "how to help someone with mental health", "mental health crisis",
        "mental health emergency", "mental health intervention"
    ]
    
    # Check if the input is asking for mental health first aid information
    if any(keyword in input_text for keyword in mhfa_keywords):
        return "search"
    
    # Check if any role play keywords are in the input
    if any(keyword in input_text for keyword in role_play_keywords):
        return "role_play"
    
    # Check if the input is asking for help with a specific situation
    if re.search(r"how (should|can|do) I (help|deal with|handle|approach)", input_text):
        return "role_play"
    
    # If the agent output exists and is a list
    if isinstance(state["agent_out"], list) and state["agent_out"]:
        tool = state["agent_out"][-1].tool
        
        # If the agent explicitly chose role_play
        if tool == "role_play":
            return "role_play"
        
        # If the agent chose search, but the content might benefit from role play
        if tool == "search":
            action = state["agent_out"][-1]
            if hasattr(action, 'tool_input'):
                tool_input = action.tool_input.lower()
                if any(keyword in tool_input for keyword in role_play_keywords):
                    return "role_play"
        
        return tool
    
    # Default to search if no other conditions are met
    return "search"


# def router(state: list):
#     print("> router")
#     if isinstance(state["agent_out"], list) and state["agent_out"]:
#         tool = state["agent_out"][-1].tool
#         if "role play" in state["input"].lower() or tool == "role_play":
#             return "role_play"
#         return tool
#     else:
#         return "error"

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

# def chat_completion(query):
#     prompt_text = "You have to act like a role playing bot.  Given a situation you will have to output a constructive dialogue on how to provide mental health first aid. eg if user says I've help my daughter who's feeling suicidal. You'll output a healthy conversation that shows supportive dad helping their daughter "
#     client = OpenAI(api_key=openai_api_key)

#     completion = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": prompt_text},
#             {"role": "user", "content": query}
#         ],
#         temperature=0.7,
#     )
#     return completion.choices[0].message.content

# # graph part 

# from langgraph.graph import StateGraph, END

# graph = StateGraph(AgentState)

# graph.add_node("planner_agent", run_planner_agent)
# graph.add_node("search", execute_search)
# graph.add_node("role_play", execute_role_play)  # Add the new node
# graph.add_node("error", handle_error)
# graph.add_node("rag_final_answer", rag_final_answer)

# graph.set_entry_point("planner_agent")

# graph.add_conditional_edges(
#     "planner_agent",
#     router,
#     {
#         "search": "search",
#         "role_play": "role_play",  # Add the new edge
#         "error": "error",
#         "final_answer": END
#     }
# )
# graph.add_edge("search", "rag_final_answer")
# graph.add_edge("role_play", "rag_final_answer")  # Add edge from role_play to final answer
# graph.add_edge("error", END)
# graph.add_edge("rag_final_answer", END)

# runnable = graph.compile()

# out = runnable.invoke({
#     "input": "I want to help my daughter who is feeling depressed. Perform role play and tell me how should I help her. You can output a dialogue between a father and daughter to show that",
#     "intermediate_steps": []
# })

# print(out["agent_out"])

# import pprint

# text = json.dumps(out["agent_out"], indent = 2)
# output_text = {
#     "agent_out": {text}
# }

# final_output = json.loads(out["agent_out"])
# print(json.dumps(final_output, indent=2))

