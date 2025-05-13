import base64
import io
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.model import WhisperSingleton
from app.config import settings
from typing import Optional
import logging
from app.utils.helpers import send_log_message_async
from app.routers.websocket import get_socket_group_name

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")


class Base64AudioInput(BaseModel):
    audio_base64: str  # base64 encoded audio data
    start_offset: Optional[float] = 0.0  # start offset in seconds
    socket_session_id: str = None  # session ID for WebSocket group


@router.post("/transcribe", dependencies=[Depends(verify_api_key)])
async def transcribe(payload: Base64AudioInput):
    logger.info("Received audio data for transcription")

    try:
        logger.debug("Decoding base64 audio data")
        audio_bytes = base64.b64decode(payload.audio_base64)
        if not audio_bytes:
            raise ValueError("Decoded audio is empty!")
    except (base64.binascii.Error, ValueError) as e:
        logger.error(f"Base64 decoding error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid base64 input: {str(e)}")

    try:
        audio_stream = io.BytesIO(audio_bytes)

        logger.info(f"Transcription started!")
        model = WhisperSingleton.get_model()
        socket_group_id = get_socket_group_name("whisper", payload.socket_session_id)

        try:
            segments, info = model.transcribe(
                audio_stream,
                vad_filter=True,  # Important for segmenting audio
                chunk_length=15,  # Process in 15-second chunks
                language=None,  # Optional: or specify "en", etc.
                task="transcribe",
                log_progress=True,  # Optional: logs segment processing
            )
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Transcription error: {str(e)}"
            )

        transcript = []

        try:
            for segment in segments:
                global_start = payload.start_offset + segment.start
                global_end = payload.start_offset + segment.end

                # Send each segment log
                await send_log_message_async(
                    message=f"{global_start:.2f}s -> {global_end:.2f}s: {segment.text}",
                    group_id=socket_group_id,
                    module="whisper_api",
                    scope="whisper",
                )

                transcript.append(segment.text)

            transcription = " ".join(transcript)
            logger.info("Transcription completed successfully!")
            logger.debug(f"Transcription result: {transcription}")

        except Exception as e:
            logger.error(f"Error during streaming transcription: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

        return {"transcription": transcription}
    except Exception as e:
        logger.error(f"Error processing transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        pass
