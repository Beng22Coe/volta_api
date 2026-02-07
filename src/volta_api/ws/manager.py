# volta_api/ws/manager.py
from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any, Dict, Optional, Set, DefaultDict

from fastapi import WebSocket
from volta_api.core.redis import redis_client

from .topics import channel_to_topic, topic_to_channel


class ConnectionManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()
        self.topic_subs: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self.socket_topics: DefaultDict[WebSocket, Set[str]] = defaultdict(set)
        self.auth: Dict[WebSocket, Any] = {}

        self._listener_task: Optional[asyncio.Task] = None
        self._listener_lock = asyncio.Lock()

        self._redis_channels: Set[str] = set()
        self._channels_lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)
        await self._ensure_redis_listener()

    async def disconnect(self, ws: WebSocket):
        topics = self.socket_topics.pop(ws, set())
        for t in topics:
            self.topic_subs[t].discard(ws)
            if not self.topic_subs[t]:
                self.topic_subs.pop(t, None)

        self.auth.pop(ws, None)
        self.active.discard(ws)

    def get_auth(self, ws: WebSocket) -> Optional[Any]:
        return self.auth.get(ws)

    async def set_auth(self, ws: WebSocket, ctx: Any):
        self.auth[ws] = ctx

    async def subscribe(self, ws: WebSocket, topic: str):
        self.topic_subs[topic].add(ws)
        self.socket_topics[ws].add(topic)
        await self._ensure_channel_subscribed(topic)

    async def unsubscribe(self, ws: WebSocket, topic: str):
        self.topic_subs[topic].discard(ws)
        self.socket_topics[ws].discard(topic)
        if not self.topic_subs[topic]:
            self.topic_subs.pop(topic, None)

    async def publish_local(self, topic: str, message: Dict[str, Any]):
        for ws in list(self.topic_subs.get(topic, set())):
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)

    async def _ensure_redis_listener(self):
        async with self._listener_lock:
            if self._listener_task and not self._listener_task.done():
                return
            self._listener_task = asyncio.create_task(self._redis_listener_loop())

    async def _ensure_channel_subscribed(self, topic: str):
        channel = topic_to_channel(topic)
        async with self._channels_lock:
            if channel in self._redis_channels:
                return
            self._redis_channels.add(channel)

    async def _redis_listener_loop(self):
        pubsub = redis_client.pubsub()
        subscribed: Set[str] = set()

        try:
            while True:
                async with self._channels_lock:
                    desired = set(self._redis_channels)

                to_add = desired - subscribed
                if to_add:
                    await pubsub.subscribe(*to_add)
                    subscribed |= to_add

                if subscribed:
                    msg = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0
                    )
                    if msg and msg.get("type") == "message":
                        ch = msg.get("channel")
                        data = msg.get("data")
                        if isinstance(ch, bytes):
                            ch = ch.decode("utf-8")
                        if isinstance(data, bytes):
                            data = data.decode("utf-8")

                        topic = channel_to_topic(ch)
                        try:
                            payload = json.loads(data)
                        except Exception:
                            continue

                        await self.publish_local(topic, payload)

                await asyncio.sleep(0)
        finally:
            try:
                await pubsub.close()
            except Exception:
                pass


manager = ConnectionManager()
