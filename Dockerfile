# ---------- Stage 1: Build dependencies ----------
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	TZ=Asia/Dhaka \
	PIP_NO_CACHE_DIR=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PATH=/root/.local/bin:$PATH

# Install system dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	wget \
	tzdata \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Asia/Dhaka /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# Install Python dependencies into a temp folder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ---------- Stage 2: Final runtime image ----------
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	TZ=Asia/Dhaka \
	PATH=/home/user/.local/bin:$PATH \
	HOME=/home/user \
	PYTHONPATH=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
	ffmpeg \
	redis-server \
	procps \
	supervisor \
	tzdata \
	ca-certificates \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Set timezone again for this stage
RUN ln -fs /usr/share/zoneinfo/Asia/Dhaka /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# Create non-root user
RUN useradd -m -u 1000 user

# Copy installed Python packages from builder
COPY --from=builder /root/.local $HOME/.local

# Set work directory and copy app code
WORKDIR $HOME/app
COPY --chown=user . .

# Supervisor configuration
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Make entrypoint executable
RUN chmod +x $HOME/app/entrypoint.sh

# Switch to non-root user
USER user

# Entrypoint
ENTRYPOINT ["bash", "-c", "/home/user/app/entrypoint.sh"]
