from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
from langgraph.graph import StateGraph, END

# Import necessary functions and classes from Sukoon project
from sukoon.ipynb import (
    AgentState,
    run_planner_agent,
    execute_search,
    router,
    rag_final_answer,
    handle_error,
    final_answer_tool,
    search_tool,
    planner_agent_runnable,
)

app = FastAPI(title="Sukoon API", description="API for the Sukoon mental health support system")

class SukoonRequest(BaseModel):
    input: str
    intermediate_steps: Optional[List[dict]] = []

class SukoonResponse(BaseModel):
    answer: str
    source: str

# Create and compile the graph
graph = StateGraph(AgentState)
graph.add_node("planner_agent", run_planner_agent)
graph.add_node("search", execute_search)
graph.add_node("error", handle_error)
graph.add_node("rag_final_answer", rag_final_answer)
graph.set_entry_point("planner_agent")
graph.add_conditional_edges(
    "planner_agent",
    router,
    {
        "search": "search",
        "error": "error",
        "final_answer": END
    }
)
graph.add_edge("search", "rag_final_answer")
graph.add_edge("error", END)
graph.add_edge("rag_final_answer", END)

runnable = graph.compile()

@app.post("/query", response_model=SukoonResponse)
async def process_query(request: SukoonRequest):
    try:
        out = runnable.invoke({
            "input": request.input,
            "intermediate_steps": request.intermediate_steps
        })
        
        result = json.loads(out["agent_out"])
        return SukoonResponse(answer=result["answer"], source=result["source"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Sukoon API. Use the /query endpoint to interact with the system."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)