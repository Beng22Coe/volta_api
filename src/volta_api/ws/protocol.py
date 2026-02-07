# volta_api/ws/protocol.py
from __future__ import annotations

from typing import Any, Dict, Optional


def ok(
    type_: str, request_id: Optional[str], payload: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    msg: Dict[str, Any] = {"type": type_}
    if request_id:
        msg["request_id"] = request_id
    msg["data"] = payload or {}
    return msg


def err(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    data = {"code": code, "message": message}
    if extra:
        data.update(extra)
    return ok("error", request_id, data)
