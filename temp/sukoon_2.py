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

with open("data/data_1.txt", 'r') as file:
    data = file.read().strip()

# llama-index function
def llama_index(query: str):
    
    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
        documents = SimpleDirectoryReader("data").load_data()
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
    """Searches for information on the topic of providing support."""
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

## Suicide prevention part
@tool("suicide")
def suicide_tool(query: str):
    """Suicide prevention part"""
    return chat_completion_1(query)

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
    model="gpt-4o", # compare mini and gpt4o , see the most important thing is eval. so have one loop scenario to test this and eval if loop is fine .. do this first before fixing any framework like langgraph
    openai_api_key=openai_api_key,
    temperature=0.1
)

prompt_text = """
  You are Sukoon's empathetic conversational agent, designed to support Indian college students with mental health concerns. Your primary role is to listen and empathize. Follow these guidelines:
    1. Ask one open-ended question to encourage the student to share their feelings. Example: "What's the most challenging part of what you're going through right now?"
    2. Listen actively and avoid giving immediate advice. Allow students to vent their feelings.
    3. Assess the level of distress and respond accordingly:
      a. Mild to Moderate: Offer brief encouragement. "It's okay to feel this way. I'm here for you."
      b. Moderate: Suggest simple activities. "Have you tried mindfulness or going for a walk?"
      c. Severe: Encourage professional help. Share helpline numbers: iCALL (+919152987821) and NIMHANS 14416.
    4. Response Guidelines:
      - Reinforce that change is possible. Ask: "What small step could you take today to feel better?"
      - Frame suggestions as questions: "Have you considered trying deep breathing?"
      - Remind them they're not alone: "You're brave for seeking help. People care about you."
      - Use 1-2 emojis max when they enhance the message.
      - Encourage discussing emotional journeys: "How has this situation affected your feelings?"
      - Motivate progress when needed: "What positive change would you like to see?"
      - End with feedback request: "How was your experience chatting with me today?"
    5. Keep responses under 50 words, maintain a supportive peer-like tone, and focus solely on mental and emotional health.
    6. If the conversation veers off-topic, gently redirect: "Let's focus on your well-being. What's on your mind?"
    7. Respond in Hinglish if the user communicates in Hinglish.
  Remember, your goal is to provide a safe space for students to express themselves and feel understood. Adapt your language between English and Hinglish based on the user's preference.
"""

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
    
    # Check if action is an AgentFinish
    if isinstance(action, AgentFinish):
        return {"intermediate_steps": [{"search": action.return_values.get("answer", "No answer provided")}]}
    
    tool_call = action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]
    out = search_tool.invoke(
        json.loads(tool_call["function"]["arguments"])
    )
    return {"intermediate_steps": [{"search": str(out)}]}


def execute_suicide(state: list):
    print("> execute_suicide")
    action = state["agent_out"]
    
    # Check if action is an AgentFinish
    if isinstance(action, AgentFinish):
        return {"intermediate_steps": [{"suicide": action.return_values.get("answer", "No answer provided")}]}
    
    tool_call = action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]
    out = suicide_tool.invoke(
        json.loads(tool_call["function"]["arguments"])
    )
    return {"intermediate_steps": [{"suicide": str(out)}]}


# use AI assistant for interactive chat
def chat_completion_1(query):
    client = OpenAI(api_key=openai_api_key)
    prompt_text = """  You are Sukoon's specialized suicide prevention agent for Indian college students. When activated, your primary tasks are:
        1. Implement QPR (Question, Persuade, Refer) crisis intervention techniques.
        2. Firmly but compassionately encourage immediate professional help. Use phrases like: "Your life matters. Let's get you the support you need right now."
        3. Create a safe space for the student to express their feelings. Acknowledge their pain without making assumptions.
        4. Provide suicide prevention helpline numbers in EVERY response:
        - iCALL: +919152987821
        - NIMHANS: +918046110007 or 14416
    Remember, your goal is to keep the student safe and connect them with professional help immediately. Prioritize their well-being above all else.
    Reply "TERMINATE" when the task is complete.
    """

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
    tools=[final_answer_tool, search_tool], # suicide_tool
    prompt=prompt
)

def router(state: dict):
    print("> router")
    input_text = state["input"].lower()
    
    suicide_keywords = [
        "suicide", "kill myself", "end my life", "die", "self-harm", 
        "no way out", "hopeless", "worthless", "give up", "can't go on",
        "life is not worth living", "better off dead", "want to disappear"
    ]
    # Check if any role play keywords are in the input
    if any(keyword in input_text for keyword in suicide_keywords):
        return "suicide"
    
    # Check if the input is asking for help with a specific situation
    if re.search(r"how (should|can|do) I (help|deal with|handle|approach)", input_text):
        return "suicide"
    
    # Check the agent_out
    if isinstance(state["agent_out"], AgentFinish):
        # If it's AgentFinish, we're done
        return "final_answer"
    elif isinstance(state["agent_out"], list) and state["agent_out"]:
        last_action = state["agent_out"][-1]
        if isinstance(last_action, AgentAction):
            # If it's an AgentAction, use the tool attribute
            return last_action.tool
    
    # Default to search if no other conditions are met
    return "search"

# def router(state: list):
#     print("> router")
#     if isinstance(state["agent_out"], list) and state["agent_out"]:
#         tool = state["agent_out"][-1].tool
#         if "role play" in state["input"].lower() or tool == "suicide":
#             return "suicide"
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
    
    # Check if the last state is an AgentFinish
    if isinstance(state["intermediate_steps"][-1], AgentFinish):
        context = state["intermediate_steps"][-1].return_values
    else:
        context = state["intermediate_steps"][-1]

    prompt = f"""You are a helpful assistant, answer the user's question using the
    context provided.

    CONTEXT: {context}

    QUESTION: {query}
    """
    out = final_answer_llm.invoke(prompt)
    function_call = out.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
    return {"agent_out": function_call}

def handle_error(state: list):
    print("> handle_error")
    query = state["input"]
    
    # Check if the last state is an AgentFinish
    if isinstance(state["intermediate_steps"][-1], AgentFinish):
        context = state["intermediate_steps"][-1].return_values
    else:
        context = "No context available."

    prompt = f"""You are a helpful assistant, answer the user's question.

    QUESTION: {query}
    CONTEXT: {context}
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

from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)

graph.add_node("planner_agent", run_planner_agent)
graph.add_node("search", execute_search)
graph.add_node("suicide", execute_suicide)  # Add the new node
graph.add_node("error", handle_error)
graph.add_node("rag_final_answer", rag_final_answer)

graph.set_entry_point("planner_agent")

graph.add_conditional_edges(
    "planner_agent",
    router,
    {
        "search": "search",
        "suicide": "suicide",  # Add the new edge
        "error": "error",
        "final_answer": END
    }
)
graph.add_edge("search", "rag_final_answer")
graph.add_edge("suicide", END)  # Add edge from suicide to final answer
graph.add_edge("error", END)
graph.add_edge("rag_final_answer", END)

runnable = graph.compile()

# Get user input
user_input = input("Hey, what do you need help with: ")

# Update the input in the runnable.invoke() call
out = runnable.invoke({
    "input": user_input,
    "intermediate_steps": []
})


out = runnable.invoke({
    "input": "I am stressed. help me",
    "intermediate_steps": []
})

print("Sukoon response is: \n")
print(out["agent_out"])

# import pprint

# text = json.dumps(out["agent_out"], indent = 2)
# output_text = {
#     "agent_out": {text}
# }

# final_output = json.loads(out["agent_out"])
# print(json.dumps(final_output, indent=2))

