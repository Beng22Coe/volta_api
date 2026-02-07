# volta_api/ws/constants.py

LATEST_KEY = "vehicle:{vehicle_id}:latest"
HISTORY_KEY = "vehicle:{vehicle_id}:history"
UPDATES_CH = "vehicle:{vehicle_id}:updates"
ROUTE_UPDATES_CH = "route:{route_id}:updates"
SHARING_KEY = "vehicle:{vehicle_id}:sharing"

HISTORY_TTL_SECONDS = 60 * 60  # 1 hour
HISTORY_MAX = 2000
SHARING_TTL_SECONDS = 30

SUPPORTED_TYPES = [
    "auth",
    "ping",
    "route.subscribe",
    "route.unsubscribe",
    "vehicle.subscribe",
    "vehicle.unsubscribe",
    "vehicle.location.share",
    "vehicle.location.broadcast",
]
