import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Callable

def is_alphanumeric(value: str) -> bool:
    if not isinstance(value, str): return False
    return bool(re.match(r'^[a-zA-Z0-9_ ]+$', value))

def is_valid_date(value: str, date_format: str = "%Y-%m-%d") -> bool:
    if not isinstance(value, str): return False
    try:
        datetime.strptime(value, date_format)
        return True
    except ValueError:
        return False

def is_integer(value: Any) -> bool:
    return isinstance(value, int)

def is_float(value: Any) -> bool:
    return isinstance(value, float)

VALIDATORS: Dict[str, Callable[[Any], bool]] = {
    'alphanumeric': is_alphanumeric,
    'date': is_valid_date,
    'int': is_integer,
    'float': is_float,
}

def _validate_recursive(data: Dict[str, Any], schema: Dict[str, Any], errors: Dict[str, str], path: str = ""):
    """Recursively validates a nested dictionary against a schema."""
    for key, rule in schema.items():
        current_path = f"{path}.{key}" if path else key

        # Check if the key exists in the data
        if key not in data or data[key] is None:
            # You can decide if None is an error or should be skipped.
            # For now, we'll flag it as a missing required field.
            errors[current_path] = 'Missing required field.'
            continue

        value = data[key]

        # If the rule is a dictionary, recurse into the nested object
        if isinstance(rule, dict):
            if isinstance(value, dict):
                _validate_recursive(value, rule, errors, current_path)
            else:
                errors[current_path] = 'Should be a dictionary (object).'
        # Otherwise, it's a validation rule for a field
        else:
            validator = VALIDATORS.get(rule)
            if not validator:
                errors[current_path] = f'No validator for rule: {rule}'
            elif not validator(value):
                errors[current_path] = f'Invalid format. Expected {rule}.'

def run(request: dict) -> Tuple[bool, Dict[str, str]]:
    """
    Validates fields in the request dictionary against a schema within the request.
    The request must contain a 'data' key for the object to validate and a 
    'schema' key for the validation rules.
    
    Returns (is_valid, errors_dict)
    """
    data_to_validate = request.get('data')
    schema = request.get('schema')

    if not isinstance(data_to_validate, dict):
        return False, {"error": "Request must contain a 'data' dictionary."}
    if not isinstance(schema, dict):
        return False, {"error": "Request must contain a 'schema' dictionary."}

    errors = {}
    _validate_recursive(data_to_validate, schema, errors)
    
    return len(errors) == 0, errors

# Example usage for your planner:
# Your planner should construct a request like this.
#
# example_request = {
#   "data": {
#     "character": { "first_name": "leeroy", "age": "twenty" },
#     "stats": { "hp": 100 }
#   },
#   "schema": {
#     "character": {
#       "first_name": "alphanumeric",
#       "age": "int"
#     },
#     "stats": {
#       "hp": "int"
#     }
#   }
# }
#
# is_valid, validation_errors = run(example_request)
# print(f"Is valid: {is_valid}")
# print(f"Errors: {validation_errors}")
# Expected output:
# Is valid: False
# Errors: {'character.age': 'Invalid format. Expected int.'}
