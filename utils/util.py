import json

def get_agent_route(request: dict) -> json:
    current_step_index = request['current_step'] - 1
    agent_name = request['plan'][current_step_index]['agent']
    action_name = request['plan'][current_step_index]['action']
    return json.dumps({"agent_name": agent_name,
                        "action_name": action_name})