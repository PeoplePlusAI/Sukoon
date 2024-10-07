from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langgraph.graph.message import AnyMessage, add_messages
from typing import Literal, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
from openai import OpenAI
import os 
from langchain_openai import ChatOpenAI
import yaml

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# Define the state
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

openai_api_key = os.getenv("OPENAI_API_KEY")
def load_prompts(file_path='../prompts.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

prompts = load_prompts()
# Initialize OpenAI model
# model = llm
model = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Define prompts
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a planner agent that decides which specialized agent to call based on the user's input. If the query indicates a risk of suicide or self-harm, respond with 'suicide_prevention'. Otherwise, respond with 'conversational'."),
    ("human", "{input}"),
])

conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts['empathetic_agent_prompt']),
    ("human", "{input}"),
])

suicide_prevention_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts['suicide_prevention_agent_prompt']),
    ("human", "{input}"),
])

# Define router
def route_query(state: State):
    class RouteQuery(BaseModel):
          """Route a user query to the most relevant node."""
          route: Literal["conversational", "suicide_prevention"] = Field(
              ...,
              description="Given a user question choose to route it to normal conversation or a suicide prevention.",
          )
    structured_llm_router = model.with_structured_output(RouteQuery)
    question_router = planner_prompt | structured_llm_router
    last_message = state["messages"][-1]
    resp = question_router.invoke({"input": last_message})
    return resp.route

def run_conversational_agent(state: State):
    print("Running conversational agent")
    convo_model = conversational_prompt | model
    response = convo_model.invoke(state["messages"])
    return {"messages": response}

def run_suicide_prevention_agent(state: State):
    print("Running suicide prevention agent")
    concern_model = suicide_prevention_prompt | model
    response = concern_model.invoke(state["messages"])
    return {"messages": response}

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("conversational", run_conversational_agent)
workflow.add_node("suicide_prevention", run_suicide_prevention_agent)

# Add edges
workflow.add_conditional_edges(
    START,
    route_query,
     {
        "conversational": "conversational",
        "suicide_prevention": "suicide_prevention"
     },
)
workflow.add_edge("conversational", END)
workflow.add_edge("suicide_prevention", END)

# Compile the graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Function to run a conversation turn
def chat(message: str, config: dict):
    # print("User:", message)
    result = graph.invoke({"messages": [HumanMessage(content=message)]}, config=config)
    return result["messages"][-1]

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break
        # response = chat("Hi! I'm feeling really stressed about my exams", config)
        # print("Bot:", response.content)
        response = chat(user_input, config)
        print("Sukoon:", response.content)