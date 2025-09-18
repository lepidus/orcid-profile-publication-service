import json
import hashlib
from typing import Any, Dict

VOLATILE_KEYS = {
    "timestamp"
}

def _normalize(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: _normalize(value) for key, value in sorted(data.items()) if key not in VOLATILE_KEYS}
    if isinstance(data, list):
        return [_normalize(value) for value in data]
    return data


def compute_work_hash(work_data: Dict[str, Any]) -> str:
    normalized = _normalize(work_data)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonicalize_work_json(work_data: Dict[str, Any]) -> str:
    normalized = _normalize(work_data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
