import redis
import os
import json
import gzip

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=False
)

def get_cached_offers(from_code, to_code):
    key = f"offers:{from_code}:{to_code}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(gzip.decompress(cached).decode('utf-8'))
    return None

def cache_offers(from_code, to_code, offers, ttl=60):
    key = f"offers:{from_code}:{to_code}"
    compressed = gzip.compress(json.dumps(offers).encode('utf-8'))
    redis_client.setex(key, ttl, compressed)

def cache_offer_details(offer_id, offer, ttl=300):
    key = f"offers:{offer_id}"
    redis_client.setex(key, ttl, json.dumps(offer))

def get_cached_offer_details(offer_id):
    key = f"offers:{offer_id}"
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

def create_session(user_id, ttl=900):
    session_id = str(uuid.uuid4())
    redis_client.setex(f"session:{session_id}", ttl, user_id)
    return session_id