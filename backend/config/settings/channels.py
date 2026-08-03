# Daphne
ASGI_APPLICATION = "config.asgi.application"

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://redis:6379/0?socket_timeout=10"],
        },
    },
}
