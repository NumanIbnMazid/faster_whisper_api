import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()


def run():
    log_level_env = os.getenv("LOG_LEVEL", "info")
    uvicorn.run(
        "app.asgi:app",  # Update to your actual ASGI path
        host="0.0.0.0",
        port=int(os.getenv("PORT", 7860)),
        reload=True,
        workers=1,
        timeout_keep_alive=60,
        ws_ping_interval=30,
        ws_ping_timeout=99999,
        log_level=log_level_env.lower(),  # <-- lowercase for uvicorn
        lifespan="off",
    )


if __name__ == "__main__":
    run()
