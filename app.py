import importlib
import json
import logging
from utils.util import get_agent_route

logging.basicConfig(level=logging.INFO)

async def execute_agent(agent_request: dict) -> dict:
    """
    Dynamically imports and calls the specified agent.
    """
    try:
        logging.info(f"Executing agent: {agent_request['step']['agent']} with action: {agent_request['step']['action']}")
        agent_module = importlib.import_module(f"agents.{agent_request['step']['agent']}.{agent_request['step']['agent']}")
        agent_response = await agent_module.run(agent_request)
        return agent_response
    except ImportError as e:
        logging.error(f"Error importing agent: {e}")
        return { "error": f"Error importing agent: {e}" }
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return { "error": f"An error occurred: {e}" }
