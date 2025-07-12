import importlib
import json


def run(request: dict, step: json):
    """
    The main entry point for the agent.
    """
    sub_agent_module = importlib.import_module(f"agents.{step['agent']}.sub_agents.{step['action']}")
    # You can call sub-agents or perform other logic here
    sub_agent_response = sub_agent_module.run(request)
    return { "result": f"Agent 'character' received query: '{request}'. Sub-agent response: {sub_agent_response}" }
