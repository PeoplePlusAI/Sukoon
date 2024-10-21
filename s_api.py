from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
import uvicorn
import json
from typing import List, Optional, Dict, Any
from pprint import pformat
from langchain_core.agents import AgentAction, AgentFinish

# Import necessary functions from sukoon.py
from sukoon import chat

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sukoon", description="API for the Sukoon mental health support system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class SukoonRequest(BaseModel):
    input: str

class SukoonResponse(BaseModel):
    output: str

@app.post("/query", response_model=SukoonResponse)
async def process_query(request: SukoonRequest):
    config = {"configurable": {"thread_id": "1"}}
    user_input = request.input
    response = chat(user_input, config)
    return SukoonResponse(output=response.content)

@app.get("/")
async def root():
    return {"message": "Hi"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
