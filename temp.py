from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from typing import TypedDict, List
import os

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

# Define the state
class State(TypedDict):
    messages: List[HumanMessage | AIMessage]

# Initialize OpenAI model
model = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define prompts
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a planner agent that decides which specialized agent to call based on the user's input. If the query indicates a risk of suicide or self-harm, respond with 'suicide_prevention'. Otherwise, respond with 'conversational'."),
    ("human", "{input}"),
])

conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an empathetic conversational agent. Provide supportive responses to help relieve student stress."),
    ("human", "{input}"),
])

suicide_prevention_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a suicide prevention agent. Apply QPR (Question, Persuade, Refer) techniques and refer to trained professionals or suicide prevention helpline. Be extremely cautious and supportive."),
    ("human", "{input}"),
])

# Define node functions
def route_query(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    
    response = model.invoke([planner_prompt.format(input=last_message.content)])
    return response.content.strip().lower()

def run_conversational_agent(state: State):
    response = model.invoke([conversational_prompt] + state["messages"])
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}

def run_suicide_prevention_agent(state: State):
    response = model.invoke([suicide_prevention_prompt] + state["messages"])
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}

def should_continue(state: State):
    if len(state["messages"]) > 15:
        return "end"
    return "router"

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("router", route_query)
workflow.add_node("conversational", run_conversational_agent)
workflow.add_node("suicide_prevention", run_suicide_prevention_agent)

# Add edges
workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    lambda x: x,
    {
        "conversational": "conversational",
        "suicide_prevention": "suicide_prevention"
    }
)
workflow.add_conditional_edges(
    "conversational",
    should_continue,
    {
        "router": "router",
        "end": END
    }
)
workflow.add_edge("suicide_prevention", END)

# Compile the graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Function to run a conversation turn
def chat(message: str, config: dict):
    result = graph.invoke({"messages": [HumanMessage(content=message)]}, config=config)
    return result["messages"][-1]

# Example usage
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test"}}
    
    response = chat("Hi! I'm feeling really stressed about my exams", config)
    print("Bot:", response.content)
    
    response = chat("I don't know if I can handle this stress anymore", config)
    print("Bot:", response.content)