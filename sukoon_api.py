from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
from typing import List, Optional, Dict, Any
from pprint import pformat
from langgraph.graph import StateGraph, END
from langgraph.graph import StateGraph, END
from langchain_core.agents import AgentAction, AgentFinish
# Import necessary functions and classes from Sukoon project
from sukoon import (
    AgentState,
    run_planner_agent,
    execute_search,
    router,
    rag_final_answer,
    handle_error,
    execute_role_play,
    final_answer_tool,
    search_tool,
    planner_agent_runnable,
    role_play_tool,  # Add this import
)

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Sukoon API", description="API for the Sukoon mental health support system")

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
    intermediate_steps: Optional[List[dict]] = []

class SukoonResponse(BaseModel):
    answer: str
    source: str
    intermediate_steps: List[Dict[str, Any]]
    full_output: Dict[str, Any]

# Create and compile the graph

graph = StateGraph(AgentState)

graph.add_node("planner_agent", run_planner_agent)
graph.add_node("search", execute_search)
graph.add_node("role_play", execute_role_play)  # Add the new node
graph.add_node("error", handle_error)
graph.add_node("rag_final_answer", rag_final_answer)

graph.set_entry_point("planner_agent")

graph.add_conditional_edges(
    "planner_agent",
    router,
    {
        "search": "search",
        "role_play": "role_play",  # Add the new edge
        "error": "error",
        "final_answer": END
    }
)

graph.add_edge("search", "rag_final_answer")
graph.add_edge("role_play", END)  # earlier edge from role_play to final answer - ("role_play", "rag_final_answer")
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

        # Extract agent output
        agent_out = out.get("agent_out")

        # Handle different types of agent output
        if isinstance(agent_out, AgentFinish):
            # Extract return_values from AgentFinish
            result = agent_out.return_values
        elif isinstance(agent_out, dict):
            result = agent_out
        else:
            # If it's neither AgentFinish nor a dict, use a default structure
            result = {"answer": str(agent_out), "source": "Unknown"}

        # Format the full output
        # Remove the AgentFinish object before serialization
        out_serializable = out.copy()
        if isinstance(agent_out, AgentFinish):
            out_serializable["agent_out"] = agent_out.return_values
        else:
            out_serializable["agent_out"] = agent_out

        formatted_output = json.loads(json.dumps(out_serializable, indent=2, default=str))

        # Extract and format intermediate steps
        intermediate_steps = [
            {step: pformat(details, indent=2)}
            for step_dict in out.get("intermediate_steps", [])
            for step, details in step_dict.items()
        ]

        return SukoonResponse(
            answer=result.get("answer", "No answer provided"),
            source=result.get("source", ""),
            intermediate_steps=intermediate_steps,
            full_output=formatted_output
        )
    except Exception as e:
        # Log the error and return a more informative error response
        # logging.error(f"Error processing query: {str(e)}")
        return SukoonResponse(
            answer=f"An error occurred: {str(e)}",
            source="Error",
            intermediate_steps=[],
            full_output={"error": str(e)}
        )

# @app.post("/query", response_model=SukoonResponse)
# async def process_query(request: SukoonRequest):
#     try:
#         out = runnable.invoke({
#             "input": request.input,
#             "intermediate_steps": request.intermediate_steps
#         })
#         # Handle different types of agent output
#         if isinstance(out["agent_out"], AgentFinish):
#             result = out["agent_out"].return_values
#         elif isinstance(out["agent_out"], dict):
#             result = out["agent_out"]
#         else:
#             # If it's neither AgentFinish nor a dict, use a default structure
#             result = {"answer": str(out["agent_out"]), "source": "Unknown"}
        
#         # Format the full output
#         formatted_output = json.loads(json.dumps(out, indent=2, default=str))
        
#         # Extract and format intermediate steps
#         intermediate_steps = [
#             {step: pformat(details, indent=2)} 
#             for step_dict in out.get("intermediate_steps", [])
#             for step, details in step_dict.items()
#         ]
        
#         return SukoonResponse(
#             answer=result.get("answer", "No answer provided"),
#             source=result.get("source", ""),
#             intermediate_steps=intermediate_steps,
#             full_output=formatted_output
#         )
#     except Exception as e:
#         # Log the error and return a more informative error response
#         # logging.error(f"Error processing query: {str(e)}")
#         return SukoonResponse(
#             answer=f"An error occurred: {str(e)}",
#             source="Error",
#             intermediate_steps=[],
#             full_output={"error": str(e)}
#         )
'''
# printing in nice format
import pprint

text = json.dumps(out["agent_out"], indent = 2)
output_text = {
    "agent_out": {text}
}

final_output = json.loads(out["agent_out"])
print(json.dumps(final_output, indent=2))
# to see intermediate steps 
pprint.pprint(out, indent = 4)
'''
@app.get("/")
async def root():
    return {"message": "Welcome to the Sukoon API. Use the /query endpoint to interact with the system."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    

# example POST request to http://127.0.0.1:8000/query
'''
{
  "input": "what I should do in providing immediate care?",
  "intermediate_steps": []
}
'''

'''
Output - 
{
    "answer": "In providing immediate care for mental health first aid, you should offer a humane and supportive response to individuals experiencing distress. This involves providing immediate help until professional assistance is available or the crisis is resolved. Approach the individual with care, empathy, and respect, allowing them to open up at their own pace without pressuring them to share their story. This type of care is accessible to everyone and not limited to mental health professionals, addressing short-term crises and everyday stressors in a community-based and easily accessible manner.",
    "source": "search"
}
'''