---
title: Faster Whisper API
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: docker
sdk_version: "27.4.1Z"
python_version: "3.12"
pinned: false
---

# 🎙️ FastAPI Whisper Transcriber

A simple, production-ready FastAPI API for transcribing audio using [`faster-whisper`](https://github.com/guillaumekln/faster-whisper).  
It accepts base64-encoded audio input, supports API key authentication, and runs with Docker.

---

## 🚀 Features

- 🔐 API key protected endpoint
- 🧠 Uses `faster-whisper` for efficient transcription
- 🎧 Accepts base64-encoded audio input (wav, mp3, etc.)
- 🐳 Dockerized and ready for deployment
- 🧼 Singleton model loading for performance

---

## 📦 Requirements

- Docker (recommended)
- Python 3.8+ (if running locally)

---

## 🛠️ Local Development

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-username/fastapi-whisper-transcriber.git
    cd fastapi-whisper-transcriber
    ```

2. **Create a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a .env file**

    ```env
    MODEL_SIZE=medium
    DEVICE=cpu
    API_KEY=supersecretkey
    ```
5. **Run the server**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

## 🐳 Docker Instructions

1. **Build the Docker image**

    ```bash
    docker build -t fastapi-whisper .
    ```

2. **Run the Docker container**

    ```bash
    docker run -p 8000:8000 \
    -e MODEL_SIZE=medium \
    -e DEVICE=cpu \
    -e API_KEY=supersecretkey \
    fastapi-whisper
    ```

3. **Verify it’s working**

Visit `http://localhost:8000/docs` for the Swagger UI.
Use the `x-api-key` header to authenticate requests.


## 🧪 Sample API Request

### Python example

```python
import base64
import requests

# Load audio file and encode to base64
with open("example.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

# Send request
response = requests.post(
    "http://localhost:8000/transcribe",
    headers={"x-api-key": "supersecretkey"},
    json={"audio_base64": audio_b64, "extension": "wav"}
)

print(response.json())
```
