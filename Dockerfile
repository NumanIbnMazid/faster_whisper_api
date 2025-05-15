FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Dhaka

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	redis-server \
	supervisor \
	tzdata \
	ca-certificates \
	ffmpeg \
	wget \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Asia/Dhaka /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

ENV PYTHONPATH=/app

# Set up Supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Add the entrypoint script and make it executable
RUN chmod +x /app/entrypoint.sh

# Entrypoint
ENTRYPOINT ["bash", "-c", "/app/entrypoint.sh"]
