# volta_api/ws/store.py
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from volta_api.core.redis import redis_client
from .constants import (
    HISTORY_KEY,
    HISTORY_MAX,
    HISTORY_TTL_SECONDS,
    LATEST_KEY,
    SHARING_KEY,
    SHARING_TTL_SECONDS,
)


async def get_latest(vehicle_id: int | str) -> Optional[Dict[str, Any]]:
    key = LATEST_KEY.format(vehicle_id=vehicle_id)
    raw = await redis_client.get(key)
    if not raw:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        return json.loads(raw)
    except Exception:
        return None


async def save_latest_and_history(vehicle_id: int | str, event_msg: Dict[str, Any]):
    latest_key = LATEST_KEY.format(vehicle_id=vehicle_id)
    history_key = HISTORY_KEY.format(vehicle_id=vehicle_id)

    raw = json.dumps(event_msg)

    await redis_client.set(latest_key, raw)
    await redis_client.rpush(history_key, raw)
    await redis_client.ltrim(history_key, -HISTORY_MAX, -1)
    await redis_client.expire(history_key, HISTORY_TTL_SECONDS)


async def set_sharing(vehicle_id: int | str, enabled: bool):
    key = SHARING_KEY.format(vehicle_id=vehicle_id)
    if not enabled:
        await redis_client.delete(key)
        return
    await redis_client.set(key, "1", ex=SHARING_TTL_SECONDS)


async def refresh_sharing(vehicle_id: int | str):
    key = SHARING_KEY.format(vehicle_id=vehicle_id)
    await redis_client.expire(key, SHARING_TTL_SECONDS)


async def is_sharing_active(vehicle_id: int | str) -> bool:
    key = SHARING_KEY.format(vehicle_id=vehicle_id)
    return bool(await redis_client.exists(key))
