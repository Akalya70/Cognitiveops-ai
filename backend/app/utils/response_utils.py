"""Standard response envelope helpers and JSON (de)serialization helpers."""
import json
from datetime import datetime, date
from typing import Any


def success_response(data: Any = None, message: str = "OK"):
    """Build a standard success envelope."""
    return {"success": True, "message": message, "data": data}


def error_response(message: str, details: Any = None):
    """Build a standard error envelope."""
    return {"success": False, "message": message, "details": details}


def _json_default(obj: Any) -> str:
    """Fallback encoder for types json.dumps can't handle natively (datetimes)."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def to_json(value: Any) -> str:
    """Safely serialize a Python value to a JSON string, encoding datetimes as ISO strings."""
    if value is None:
        return json.dumps([])
    return json.dumps(value, default=_json_default)


def from_json(value: str, default: Any = None) -> Any:
    """Safely deserialize a JSON string, returning `default` on failure."""
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []
