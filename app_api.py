import os
import autogen
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

app = FastAPI()

# Configure the agents
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.7}

# Load YAML file
def load_prompts(file_path='prompts.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

prompts = load_prompts()

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

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
user = autogen.UserProxyAgent(
    name="User",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    code_execution_config={"use_docker": False},
)

agents = {
    "planner": autogen.AssistantAgent(
        name="PlannerAgent",
        system_message=prompts['planner_agent_prompt'],
        llm_config=llm_config,
    ),
    "empathetic": autogen.AssistantAgent(
        name="EmpatheticAgent",
        system_message=prompts['empathetic_agent_prompt'],
        llm_config=llm_config,
    ),
    "suicide_prevention": autogen.AssistantAgent(
        name="SuicidePreventionAgent",
        system_message=prompts['suicide_prevention_agent_prompt'],
        llm_config=llm_config,
    )
}

for agent in agents.values():
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)

groupchat = autogen.GroupChat(
    agents=[user, agents["empathetic"], agents["suicide_prevention"]],
    messages=[],
    max_round=15,
    speaker_selection_method="auto",
    allow_repeat_speaker=False, # enable True to have conversation with same agent
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Pydantic models for request and response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# API endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_input = request.message
    if user_input.lower() in ['exit', 'quit', 'end', 'bye']:
        return ChatResponse(response="Thank you for using the Mental Health Assistant. Take care!")
    
    # Start conversation with planner agent to decide which agent to use. check generate_response method, else use generate_reply
    planner_response = agents["planner"].generate_reply(
        f"User input: {user_input}\nAssess the situation and decide which agent (empathetic or suicide_prevention) should handle this input. Only return the name of the chosen agent.",
    )
    
    # Extract the chosen agent name
    chosen_agent = planner_response.lower().strip()
    if chosen_agent not in ["empathetic", "suicide_prevention"]:
        chosen_agent = "empathetic"  # Default to empathetic agent if planner's response is unclear
    
    # Generate response from the chosen agent
    agent_response = agents[chosen_agent].generate_response(
        f"User input: {user_input}\nRespond to the user's input appropriately.",
    )
    
    return ChatResponse(response=agent_response)

@app.get("/")
async def root():
    return {"message": "Welcome to the Mental Health Assistant API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)