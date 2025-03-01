from server.settings.components import config

REDIS_SSL: bool = config("REDIS_SSL", cast=bool, default=False)
REDIS_PREFIX: str = config("REDIS_PREFIX", default="pet-alert")

REDIS_PROTOCOL: str = "rediss" if REDIS_SSL else "redis"

# Example: redis://127.0.0.1:6379/0
REDIS_URL: str = (
    f"{REDIS_PROTOCOL}://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}"
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": REDIS_PREFIX,
    }
}
