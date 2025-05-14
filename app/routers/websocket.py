from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState
import logging
import asyncio
import json
from app.sockets.connection_manager import RedisConnectionManager

router = APIRouter()
logger = logging.getLogger(__name__)
redis_manager = RedisConnectionManager()

PING_INTERVAL = 20
groups: dict[str, set[WebSocket]] = {}


def get_socket_group_name(group_name: str, session_id: str) -> str:
    valid_group_names = ["whisper"]
    if group_name not in valid_group_names:
        raise ValueError(
            f"Invalid group name: {group_name}. Valid names are: {valid_group_names}"
        )
    if not session_id:
        raise ValueError("Session ID cannot be None or empty.")
    return f"{group_name}_group_{session_id}"


@router.websocket("/ws/{group_name}")
async def websocket_endpoint(
    websocket: WebSocket, group_name: str, session_id: str = Query(...)
):
    group_id = None
    ping_task = None
    listener_task = None

    await websocket.accept()

    try:
        # Origin verification
        origin = websocket.headers.get("origin")
        allowed_origins = ["http://localhost:3000", "https://apps.nim23.com"]
        if origin not in allowed_origins:
            logger.warning(f"❌ Forbidden origin: {origin}")
            await websocket.close(code=1008)
            return

        # Setup Redis + group
        group_id = get_socket_group_name(group_name, session_id)
        await redis_manager.connect()
        pubsub = await redis_manager.subscribe(group_id)

        client_ip = websocket.client.host
        logger.info(f"🔌 WebSocket connected - Group: {group_id}, IP: {client_ip}")

        # Track connection
        groups.setdefault(group_id, set()).add(websocket)

        # Start background tasks
        ping_task = asyncio.create_task(send_keep_alive(websocket))
        listener_task = asyncio.create_task(redis_listener(websocket, pubsub))

        # Send welcome message
        await websocket.send_json(
            {
                "message": f"🔵 Connected to {group_name} WebSocket",
                "group": group_id,
                "client_ip": client_ip,
            }
        )

        # Main loop: receive messages
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload.get("type") == "ready":
                logger.info(f"🟢 Ready from IP {client_ip} [Session: {session_id}]")
                await redis_manager.publish(
                    group_id,
                    {
                        "type": "message",
                        "data": payload,
                    },
                )

    except WebSocketDisconnect:
        logger.info(f"🔴 Disconnected - Group: {group_id}, IP: {websocket.client.host}")
    except Exception as e:
        logger.exception(f"❌ WebSocket error: {e}")
    finally:
        if ping_task:
            ping_task.cancel()
        if listener_task:
            listener_task.cancel()

        # Clean up group membership
        if group_id and websocket in groups.get(group_id, set()):
            groups[group_id].remove(websocket)

        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

        logger.debug(f"🧹 Cleanup complete for group: {group_id}")


async def send_keep_alive(websocket: WebSocket):
    try:
        while True:
            await asyncio.sleep(PING_INTERVAL)
            await websocket.send_json({"type": "ping"})
    except asyncio.CancelledError:
        logger.debug("🛑 Keep-alive cancelled")
    except Exception as e:
        logger.error(f"🛑 Keep-alive error: {e}")


async def redis_listener(websocket: WebSocket, pubsub):
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    await websocket.send_text(msg["data"])
                except Exception as e:
                    logger.warning(f"💥 Failed to forward Redis message: {e}")
                    break
    except asyncio.CancelledError:
        logger.debug("🛑 Redis listener cancelled")
