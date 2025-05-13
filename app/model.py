import logging
from faster_whisper import WhisperModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class WhisperSingleton:
    _model_instance = None

    @classmethod
    def get_model(cls):
        if cls._model_instance is None:
            logger.info(
                f"🟡 [WhisperSingleton] Loading model: {settings.MODEL_SIZE} on {settings.DEVICE}"
            )
            try:
                cls._model_instance = WhisperModel(
                    settings.MODEL_SIZE, device=settings.DEVICE
                )
                logger.info("✅ [WhisperSingleton] Model loaded successfully")
            except Exception as e:
                logger.error(f"🚫 [WhisperSingleton] Failed to load model: {e}")
                raise
        else:
            logger.info("🟢 [WhisperSingleton] Returning existing model instance")
        return cls._model_instance
