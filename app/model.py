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
                logger.info(
                    f"✅ [WhisperSingleton] Model loaded successfully. Model: {settings.MODEL_SIZE} on {settings.DEVICE}"
                )
            except Exception as e:
                logger.error(f"🚫 [WhisperSingleton] Failed to load model: {e}")
                raise
        else:
            logger.info(
                f"🟢 [WhisperSingleton] Returning existing model instance. Model: {settings.MODEL_SIZE} on {settings.DEVICE}"
            )
        return cls._model_instance
