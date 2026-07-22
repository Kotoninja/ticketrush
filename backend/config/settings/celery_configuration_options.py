from config.env import env


CELERY = {
    "broker_url": env("CELERY_BROKER_URL"),
    "result_backend": env("CELERY_RESULT_BACKEND"),
    "result_extended": True,
}
