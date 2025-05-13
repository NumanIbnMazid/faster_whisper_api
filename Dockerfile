FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

ENV PYTHONPATH=/app

# Make the uvicorn.sh script executable
RUN chmod +x uvicorn.sh

CMD ["bash", "./uvicorn.sh"]
