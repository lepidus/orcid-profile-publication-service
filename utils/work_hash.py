import json
import hashlib
from typing import Any, Dict

VOLATILE_KEYS = {
    "timestamp"
}

def _normalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in sorted(obj.items()) if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [_normalize(v) for v in obj]
    return obj


def compute_work_hash(work_data: Dict[str, Any]) -> str:
    normalized = _normalize(work_data)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonicalize_work_json(work_data: Dict[str, Any]) -> str:
    normalized = _normalize(work_data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
