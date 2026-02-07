# volta_api/vehicles/ws.py
from __future__ import annotations

import json
import time
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from volta_api.core.redis import redis_client

from volta_api.ws.auth import can_publish, verify_token
from volta_api.ws.constants import SUPPORTED_TYPES
from volta_api.ws.manager import manager
from volta_api.ws.protocol import err, ok
from volta_api.ws.store import (
    is_sharing_active,
    refresh_sharing,
    save_latest_and_history,
    set_sharing,
)
from volta_api.ws.topics import topic_for_route
from volta_api.vehicles.service import get_vehicle_by_id
from volta_api.routes.service import get_route_by_id

router = APIRouter(prefix="/volta/ws", tags=["vehicles"])


@router.websocket("")
async def vehicle_ws(ws: WebSocket):
    """
    One WS endpoint:
    - client authenticates (auth)
    - commuters subscribe to routes (route.subscribe)
    - drivers/devices broadcast location (vehicle.location.broadcast)
    - server broadcasts updates to subscribers (vehicle.location.update)
    """
    await manager.connect(ws)

    try:
        while True:
            try:
                raw = await ws.receive_text()
            except Exception:
                await ws.send_json(
                    err("BAD_REQUEST", "Unable to read message text", None)
                )
                continue

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError as exc:
                await ws.send_json(
                    err(
                        "BAD_REQUEST",
                        "Invalid JSON format",
                        None,
                        extra={"detail": str(exc)},
                    )
                )
                continue

            if not isinstance(msg, dict):
                await ws.send_json(
                    err("BAD_REQUEST", "Message must be a JSON object", None)
                )
                continue

            msg_type = msg.get("type")
            request_id = msg.get("request_id")
            payload = msg.get("payload") or {}

            # ---- AUTH ----
            if msg_type == "auth":
                token = payload.get("token")
                ctx = await verify_token(token)
                if not ctx:
                    await ws.send_json(err("UNAUTHORIZED", "Invalid token", request_id))
                    await ws.close(code=1008)
                    return
                await manager.set_auth(ws, ctx)
                await ws.send_json(
                    ok(
                        "auth.ok",
                        request_id,
                        {"user_id": ctx.user_id, "role": ctx.role},
                    )
                )
                continue

            # ---- PING ----
            if msg_type == "ping":
                await ws.send_json(ok("pong", request_id, {"ts": int(time.time())}))
                continue

            # ---- SUBSCRIBE ROUTE ----
            if msg_type == "route.subscribe":
                route_id = payload.get("route_id")

                if route_id is None:
                    await ws.send_json(
                        err("BAD_REQUEST", "route_id is required", request_id)
                    )
                    continue

                try:
                    route_id = int(route_id)
                except (TypeError, ValueError):
                    await ws.send_json(
                        err("BAD_REQUEST", "route_id must be an integer", request_id)
                    )
                    continue

                route = await get_route_by_id(route_id)
                if not route:
                    await ws.send_json(err("NOT_FOUND", "Route not found", request_id))
                    continue

                topic = topic_for_route(route_id)
                await manager.subscribe(ws, topic)
                await ws.send_json(
                    ok("route.subscribe.ok", request_id, {"route_id": route_id})
                )
                continue

            # ---- UNSUBSCRIBE ROUTE ----
            if msg_type == "route.unsubscribe":
                route_id = payload.get("route_id")

                if route_id is None:
                    await ws.send_json(
                        err("BAD_REQUEST", "route_id is required", request_id)
                    )
                    continue

                try:
                    route_id = int(route_id)
                except (TypeError, ValueError):
                    await ws.send_json(
                        err("BAD_REQUEST", "route_id must be an integer", request_id)
                    )
                    continue

                topic = topic_for_route(route_id)
                await manager.unsubscribe(ws, topic)
                await ws.send_json(
                    ok("route.unsubscribe.ok", request_id, {"route_id": route_id})
                )
                continue

            # ---- SHARE LOCATION ----
            if msg_type == "vehicle.location.share":
                ctx = manager.get_auth(ws)
                if not ctx:
                    await ws.send_json(
                        err(
                            "UNAUTHORIZED",
                            "Authenticate first with type=auth",
                            request_id,
                        )
                    )
                    continue

                vehicle_id = payload.get("vehicle_id")
                enabled = payload.get("enabled", True)

                if vehicle_id is None:
                    await ws.send_json(
                        err("BAD_REQUEST", "vehicle_id is required", request_id)
                    )
                    continue

                try:
                    vehicle_id = int(vehicle_id)
                except (TypeError, ValueError):
                    await ws.send_json(
                        err("BAD_REQUEST", "vehicle_id must be an integer", request_id)
                    )
                    continue

                if not await can_publish(ctx, vehicle_id):
                    await ws.send_json(
                        err(
                            "FORBIDDEN",
                            "Not allowed to share for this vehicle",
                            request_id,
                        )
                    )
                    continue

                await set_sharing(vehicle_id, bool(enabled))
                await ws.send_json(
                    ok(
                        "vehicle.location.share.ok",
                        request_id,
                        {"vehicle_id": vehicle_id, "enabled": bool(enabled)},
                    )
                )
                continue

            # ---- BROADCAST LOCATION ----
            if msg_type == "vehicle.location.broadcast":
                ctx = manager.get_auth(ws)
                if not ctx:
                    await ws.send_json(
                        err(
                            "UNAUTHORIZED",
                            "Authenticate first with type=auth",
                            request_id,
                        )
                    )
                    continue

                vehicle_id = payload.get("vehicle_id")
                lat = payload.get("lat")
                lng = payload.get("lng")

                if vehicle_id is None or lat is None or lng is None:
                    await ws.send_json(
                        err(
                            "BAD_REQUEST",
                            "vehicle_id, lat, lng are required",
                            request_id,
                            extra={
                                "expected": {
                                    "vehicle_id": "integer",
                                    "lat": "number",
                                    "lng": "number",
                                }
                            },
                        )
                    )
                    continue

                try:
                    vehicle_id = int(vehicle_id)
                except (TypeError, ValueError):
                    await ws.send_json(
                        err("BAD_REQUEST", "vehicle_id must be an integer", request_id)
                    )
                    continue

                if not await is_sharing_active(vehicle_id):
                    await ws.send_json(
                        err(
                            "SHARING_NOT_ACTIVE",
                            "Start sharing before broadcasting location",
                            request_id,
                        )
                    )
                    continue

                if not await can_publish(ctx, vehicle_id):
                    await ws.send_json(
                        err(
                            "FORBIDDEN",
                            "Not allowed to broadcast for this vehicle",
                            request_id,
                        )
                    )
                    continue

                vehicle = await get_vehicle_by_id(vehicle_id)
                if not vehicle:
                    await ws.send_json(
                        err("NOT_FOUND", "Vehicle not found", request_id)
                    )
                    continue

                event: Dict[str, Any] = {
                    "type": "vehicle.location.update",
                    "data": {
                        "vehicle_id": vehicle_id,
                        "plate_number": vehicle.plate_number,
                        "route_id": vehicle.route_id,
                        "lat": float(lat),
                        "lng": float(lng),
                        "heading": payload.get("heading"),
                        "speed_mps": payload.get("speed_mps"),
                        "accuracy_m": payload.get("accuracy_m"),
                        "recorded_at": payload.get("recorded_at"),
                        "received_at": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        ),
                    },
                }

                await save_latest_and_history(vehicle_id, event)
                channel = f"vehicle:{vehicle_id}:updates"
                await redis_client.publish(channel, json.dumps(event))
                if vehicle.route_id is not None:
                    route_channel = f"route:{vehicle.route_id}:updates"
                    await redis_client.publish(route_channel, json.dumps(event))
                await refresh_sharing(vehicle_id)

                await ws.send_json(
                    ok("vehicle.location.ack", request_id, {"status": "ok"})
                )
                continue

            await ws.send_json(
                err(
                    "UNKNOWN_TYPE",
                    f"Unknown type: {msg_type}",
                    request_id,
                    extra={"supported": SUPPORTED_TYPES},
                )
            )

    except WebSocketDisconnect:
        await manager.disconnect(ws)
    except Exception:
        await manager.disconnect(ws)
        try:
            await ws.close(code=1011)
        except Exception:
            pass
