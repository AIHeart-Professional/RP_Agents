from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import inspect
import importlib

# --- Tool Imports ---
# We will now import dynamically, so these static imports are no longer needed.

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "my_game"
CHARACTER_COLLECTION = "characters"

# --- State Definition ---
class CharacterOrchestratorState(TypedDict):
    """Represents the state of our dynamic workflow."""
    plan: List[Dict[str, str]]
    original_request: Dict[str, Any]
    current_step: int
    results: List[Any]
    error: Optional[str]

# --- Node Definition ---
def execute_step(state: CharacterOrchestratorState) -> CharacterOrchestratorState:
    """
    Executes the current step from the plan by dynamically importing the tool
    and passing the original request state to it.
    """
    if state.get("error"):
        return state  # Skip if already in an error state

    plan = state["plan"]
    step_index = state["current_step"]
    
    if step_index >= len(plan):
        state["error"] = "Plan finished, but graph continued."
        return state

    current_plan_item = plan[step_index]
    tool_name = current_plan_item["tool"]
    action_name = current_plan_item["action"]
    
    print(f"---EXECUTING: {tool_name}.{action_name} (Step {step_index + 1}/{len(plan)})---")

    try:
        # Dynamically import the tool module
        tool_module_path = f"tools.{tool_name}.{action_name}"
        tool_module = importlib.import_module(tool_module_path)
        
        # The tool function is assumed to be named 'run' inside the module
        tool_function = getattr(tool_module, "run")

        # Call the tool, passing the original request directly.
        # All tools must now be designed to accept a single dictionary argument.
        result = tool_function(state["original_request"], state["results"])
        state["results"].append(result)

    except ModuleNotFoundError:
        state["error"] = f"Tool module not found at '{tool_module_path}.py'. Please check the path and file name."
    except AttributeError:
        state["error"] = f"Could not find a 'run' function inside '{tool_module_path}.py'."
    except Exception as e:
        state["error"] = f"Error executing step {step_index} ({tool_name}.{action_name}): {e}"
    
    state["current_step"] += 1
    return state

# --- Edge Logic ---
def should_continue(state: CharacterOrchestratorState) -> str:
    """Determines if the workflow should continue to the next step or end."""
    if state.get("error"):
        print(f"---ERROR ENCOUNTERED: {state['error']}---")
        return "end"
    if state["current_step"] >= len(state["plan"]):
        print("---PLAN COMPLETE---")
        return "end"
    return "continue"

# --- Build the Graph ---
workflow = StateGraph(CharacterOrchestratorState)

workflow.add_node("execute_step", execute_step)
workflow.set_entry_point("execute_step")

workflow.add_conditional_edges(
    "execute_step",
    should_continue,
    {
        "continue": "execute_step",
        "end": END
    }
)

# Compile the graph
character_orchestrator = workflow.compile()

# --- Main Runner ---
async def run_orchestrator(request: dict, details: dict, user_id: str, server_id: str) -> CharacterOrchestratorState:
    """
    Runs the orchestrator with a given request.
    """
    plan = details.get("steps", [])
    if not plan:
        return {"error": "No plan found in the request."}

    initial_state = {
        "plan": plan,
        "original_request": request,
        "current_step": 0,
        "results": [],
        "error": None
    }
    
    # The invoke method is synchronous. If your tools were async, you'd use ainvoke.
    final_state = character_orchestrator.invoke(initial_state)
    return final_state