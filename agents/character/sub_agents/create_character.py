from tools.universal_tools.validate_fields_tool import validate_fields
# Placeholder for the sub-agent logic

def run(request: dict):
    """
    The main entry point for the character creation sub-agent.
    Validates the request against a predefined schema and returns the result.
    """
    

    # Validate the request against the schema
    is_valid, errors = validate_fields(request)

    if is_valid:
        return {"status": "success", "message": "Character created successfully."}
    else:
        return {"status": "error", "errors": errors}