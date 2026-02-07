# volta_api/ws/auth.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from volta_api.core.security import verify_access_token
from volta_api.users.service import get_user_by_public_id
from volta_api.vehicles.service import get_vehicle_by_id, get_vehicle_user
from volta_api.ws.store import is_sharing_active

PUBLISH_ROLES = {"driver", "owner", "conductor"}


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    role: str


async def verify_token(token: str) -> Optional[AuthContext]:
    if not token:
        return None

    user_id = verify_access_token(token)
    if not user_id:
        return None

    user = await get_user_by_public_id(user_id)
    if not user or not user.is_active:
        return None

    return AuthContext(user_id=user.public_id, role=user.role)


async def can_subscribe(
    ctx: Optional[AuthContext],
    vehicle_id: int,
    *,
    session_id: Optional[str],
    share_token: Optional[str],
) -> bool:
    if ctx and ctx.role == "admin":
        return True

    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        return False

    if await is_sharing_active(vehicle_id):
        return True

    if ctx:
        vehicle_user = await get_vehicle_user(vehicle_id, ctx.user_id)
        if vehicle_user:
            return True

    if share_token or session_id:
        return False

    return False


async def can_publish(ctx: AuthContext, vehicle_id: int) -> bool:
    if ctx.role == "admin":
        return True

    vehicle_user = await get_vehicle_user(vehicle_id, ctx.user_id)
    if not vehicle_user:
        return False

    return vehicle_user.role in PUBLISH_ROLES
