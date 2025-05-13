import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MODEL_SIZE: str = os.getenv("MODEL_SIZE", "base")
    DEVICE: str = os.getenv("DEVICE", "cpu")
    API_KEY: str = os.getenv("API_KEY", "changeme")

settings = Settings()
