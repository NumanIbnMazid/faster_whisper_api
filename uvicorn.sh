#!/bin/bash
chmod +x uvicorn.sh
exec uvicorn app.main:app --host 0.0.0.0 --port 7860
