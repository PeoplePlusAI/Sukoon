from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_openai_tools_agent
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]

# Initialize OpenAI model
model = ChatOpenAI(model="gpt-4o", temperature=0.1)

# Define agents

# Planner/Router Agent
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a planner agent that decides which specialized agent to call based on the user's input. If the query mentions suicide or hints towards it, direct to the Suicide Prevention Agent. Otherwise, direct to the Empathetic Conversational Agent."),
    ("human", "{input}"),
])
planner_agent = create_openai_tools_agent(model, [], planner_prompt)

# Empathetic Conversational Agent
conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an empathetic conversational agent. Provide supportive responses to help relieve student stress. Use the RAG tool if needed to retrieve relevant information."),
    ("human", "{input}"),
])
conversational_agent = create_openai_tools_agent(model, [], conversational_prompt)

# Suicide Prevention Agent
suicide_prevention_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a suicide prevention agent. Apply QPR (Question, Persuade, Refer) techniques and refer to trained professionals or suicide prevention helpline. Be extremely cautious and supportive."),
    ("human", "{input}"),
])
suicide_prevention_agent = create_openai_tools_agent(model, [], suicide_prevention_prompt)

# Define node functions

def route_query(state):
    messages = state['messages']
    last_message = messages[-1]
    
    response = planner_agent.invoke({"input": last_message})
    if "suicide" in response.lower() or "self-harm" in response.lower():
        return "suicide_prevention"
    else:
        return "conversational"

def run_conversational_agent(state):
    messages = state['messages']
    last_message = messages[-1]
    
    response = conversational_agent.invoke({"input": last_message})
    return {"messages": [response]}

def run_suicide_prevention_agent(state):
    messages = state['messages']
    last_message = messages[-1]
    
    response = suicide_prevention_agent.invoke({"input": last_message})
    return {"messages": [response]}

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("route", route_query)
workflow.add_node("conversational", run_conversational_agent)
workflow.add_node("suicide_prevention", run_suicide_prevention_agent)

# Add edges
workflow.set_entry_point("route")
workflow.add_conditional_edges(
    "route",
    lambda x: x,
    {
        "conversational": "conversational",
        "suicide_prevention": "suicide_prevention"
    }
)
workflow.add_edge("conversational", END)
workflow.add_edge("suicide_prevention", END)

# Compile the graph
app = workflow.compile()

# Function to run a conversation turn
def chat(message: str, config: dict):
    result = app.invoke({"messages": [message]}, config=config)
    return result["messages"][-1]

# Example usage
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test"}}
    
    response = chat("I'm feeling really stressed about my exams", config)
    print("Bot:", response)
    
    response = chat("I don't see any point in living anymore", config)
    print("Bot:", response)