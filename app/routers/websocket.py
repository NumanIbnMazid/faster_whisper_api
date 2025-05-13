from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory connection store (can be replaced with Redis)
groups = {}


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
    websocket: WebSocket,
    group_name: str,
    session_id: str = Query(...),
):
    logger.debug(f"🔌 WebSocket connection request: {group_name} with session ID: {session_id}")
    group_id = None
    await websocket.accept()  # Accept early to allow origin check and custom closing

    try:
        origin = websocket.headers.get("origin")
        allowed_origins = ["http://localhost:3000", "https://apps.nim23.com"]
        logger.debug(f"🔍 WebSocket Origin: {origin}")
        if origin not in allowed_origins:
            logger.warning(f"❌ Forbidden origin: {origin}")
            await websocket.close(code=1008)
            return

        group_id = get_socket_group_name(group_name, session_id)
        logger.debug(f"🟢 WebSocket connected to group: {group_id}")

        if group_id not in groups:
            groups[group_id] = set()
        groups[group_id].add(websocket)

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        logger.debug(f"🚫 WebSocket disconnected from group: {group_id}")
        if group_id and group_id in groups:
            groups[group_id].discard(websocket)
            if not groups[group_id]:
                del groups[group_id]

    except Exception as e:
        logger.error(f"🛑 WebSocket connection error: {e}")
        if websocket.client_state.name != "CONNECTED":
            logger.debug("🛑 WebSocket was not accepted; skipping close.")
        else:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
