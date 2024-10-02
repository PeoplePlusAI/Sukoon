from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from typing import TypedDict
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
class State(MessagesState):
    summary: str = ""

# Initialize OpenAI model
model = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define the llama_index tool
def llama_index(query: str):
    """Use this tool to retrieve relevant information from the knowledge base."""
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
    return {"messages": str(response)}


tools = [llama_index]
# Bind tools to the model for the conversational agent
llm_with_tools = model.bind_tools(tools)
# Define agents

# Planner/Router Agent
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a planner agent that decides which specialized agent to call based on the user's input. If the query indicates a risk of suicide or self-harm, direct to the Suicide Prevention Agent. Otherwise, direct to the Empathetic Conversational Agent."),
    ("human", "{input}"),
])

# Empathetic Conversational Agent
conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an empathetic conversational agent. Provide supportive responses to help relieve student stress. Use the llama_index tool if needed to retrieve relevant information."),
    ("human", "{input}"),
])

# Suicide Prevention Agent
suicide_prevention_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a suicide prevention agent. Apply QPR (Question, Persuade, Refer) techniques and refer to trained professionals or suicide prevention helpline. Be extremely cautious and supportive."),
    ("human", "{input}"),
])

# Define node functions

def route_query(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    
    # Corrected line using format_messages()
    formatted_messages = planner_prompt.format_messages(input=last_message.content)
    response = model.invoke(formatted_messages)
    print(response)
    # final = response.content.strip().lower()
    state["messages"] = response.content
    return {"messages": response.content}
    # return response

def run_conversational_agent(state):
    summary = state.get("summary", "")
    if summary:
        # Include the summary as a system message
        system_message = SystemMessage(content=f"Summary of conversation earlier: {summary}")
        messages = [system_message] + state["messages"]
    else:
        messages = state["messages"]
    
    # Format the conversational prompt with the latest user message
    last_message = state["messages"][-1]
    formatted_messages = conversational_prompt.format_messages(input=last_message.content)
    
    # Combine messages and formatted prompt
    full_messages = messages + formatted_messages
    response = model.invoke(full_messages)
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}


def run_suicide_prevention_agent(state):
    # Format the suicide prevention prompt with the latest user message
    last_message = state["messages"][-1]
    formatted_messages = suicide_prevention_prompt.format_messages(input=last_message.content)
    
    # Combine any prior messages if necessary
    messages = state["messages"] + formatted_messages
    response = model.invoke(messages)
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}


def summarize_conversation(state):
    if state['summary']:
        summary_message = (
            f"This is a summary of the conversation to date: {state.summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)
    # Update the state's summary with the new summary
    state["summary"] = response.content
    return {}  # Return an empty dict or the updated state if necessary

# Add a new function to handle the routing after the conversational agent
def should_continue(state):
    if len(state["messages"]) > 15:
        return "end"
    if len(state["messages"]) > 6:
        return "summarize_conversation"
    return "router"

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("router", route_query)
workflow.add_node("conversational", run_conversational_agent)
workflow.add_node("suicide_prevention", run_suicide_prevention_agent)
workflow.add_node("summarize_conversation", summarize_conversation)
workflow.add_node("should_continue", should_continue)

# Define edges and conditional edges
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
    tools_condition,
    {
        "continue": "should_continue",  # Use the node name as a string
        "tools": "conversational"
    }
)
workflow.add_conditional_edges(
    "should_continue",
    lambda x: x,
    {
        "router": "router",
        "summarize_conversation": "summarize_conversation",
        "end": END
    }
)
workflow.add_edge("suicide_prevention", END)
workflow.add_edge("summarize_conversation", "router")

# Compile the graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Function to run a conversation turn
def chat(message: str, config: dict):
    msg = HumanMessage(content=message)
    # print(msg)
    result = graph.invoke({"messages": [msg]}, config=config)
    return result["messages"][-1]

# Example usage
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test"}}
    
    response = chat("Hi! I'm feeling really stressed about my exams", config)
    print("Bot:", response.content)
    
    response = chat("I don't know if I can handle this stress anymore", config)
    print("Bot:", response.content)