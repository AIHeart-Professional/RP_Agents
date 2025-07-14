import json
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from app import execute_agent

app = FastAPI()

# --- Pydantic Models ---
# Define a model that exactly matches the structure of the JSON being sent.

class Step(BaseModel):
    agent: str
    action: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)  # This will be the 'plan' from the orchestrator    

class UserInfo(BaseModel):
    user_id: str
    server_id: str

class AgentRequest(BaseModel):
    request: Dict[str, Any]  # This will be the 'details' from the orchestrator
    step: Step
    user_info: UserInfo
    
@app.post("/agent/invoke_agent")
async def interpret_agent(agent_request: AgentRequest):
    """
    An endpoint to invoke a specific agent with a query.
    """
    result = await execute_agent(agent_request.model_dump())
    return result

