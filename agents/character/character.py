import importlib
import json
from orchestrators.character.character_orchestrator import run_orchestrator


async def run(agent_request: dict) -> dict:
    """
    The main entry point for the agent.
    """
    results = await run_orchestrator(agent_request['request'], agent_request['step'], agent_request['user_id'], agent_request['server_id'])
    return { "result": f"Agent 'character' received query: '{agent_request['request']}'. Sub-agent response: {results}" }
