import json
from app.routers.websocket import groups  # Adjust import if needed
import uuid

async def send_log_message_async(
    *,
    message,
    group_id: str,
    type: str = "event",
    module: str = "common",
    scope: str = None,
    sender: str = "server",
    **kwargs,
):
    if group_id not in groups:
        return  # No connected clients for this group
    
    log_id = str(uuid.uuid4())
    payload = {
        "type": "send.log",
        "id": log_id,
        "message": {
            "type": type,
            "sender": sender,
            "module": module,
            "scope": scope,
            "message": message,
            **kwargs,
        },
    }

    for websocket in list(groups[group_id]):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            groups[group_id].discard(websocket)
