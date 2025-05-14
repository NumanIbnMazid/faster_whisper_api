from redis.asyncio import Redis
import json


class RedisConnectionManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Redis | None = None

    async def connect(self):
        if self.redis is None:
            self.redis = Redis.from_url(self.redis_url, decode_responses=True)

    async def publish(self, channel: str, message: dict | str):
        await self.connect()
        if isinstance(message, dict):
            message = json.dumps(message)
        await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
        await self.connect()
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
