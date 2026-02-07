# volta_api/ws/topics.py
from __future__ import annotations

from .constants import ROUTE_UPDATES_CH, UPDATES_CH


def topic_for_vehicle(vehicle_id: int | str) -> str:
    return f"vehicle:{vehicle_id}"


def topic_for_route(route_id: int | str) -> str:
    return f"route:{route_id}"


def topic_to_channel(topic: str) -> str:
    if topic.startswith("vehicle:"):
        vehicle_id = topic.split("vehicle:", 1)[1]
        return UPDATES_CH.format(vehicle_id=vehicle_id)
    if topic.startswith("route:"):
        route_id = topic.split("route:", 1)[1]
        return ROUTE_UPDATES_CH.format(route_id=route_id)
    return topic


def channel_to_topic(channel: str) -> str:
    if channel.endswith(":updates") and channel.startswith("vehicle:"):
        vehicle_id = channel[len("vehicle:") : -len(":updates")]
        return topic_for_vehicle(vehicle_id)
    if channel.endswith(":updates") and channel.startswith("route:"):
        route_id = channel[len("route:") : -len(":updates")]
        return topic_for_route(route_id)
    return channel
