from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict, Annotated
import uvicorn

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

@app.post("/query", response_model = SukoonResponse)
async def process_query(request: SukoonRequest):
    config = {"configurable": {"thread_id":"1"}}
    user_input = request.input
    response = chat(user_input, config)
    return SukoonResponse(output = response.content)
    
@app.get("/")
async def root():
    return {"message": "Welcome to the Sukoon API. Use the /query endpoint to interact with the system."}

if __name__ == "__main__":
    uvicorn.run(app, host = "127.0.0.1", port = 8001)