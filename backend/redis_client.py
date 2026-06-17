import os
import redis

from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Single Redis connection shared across the app
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
