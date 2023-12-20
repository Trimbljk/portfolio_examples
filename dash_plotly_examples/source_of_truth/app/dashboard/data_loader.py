import redis
from celery import Celery

from .constants import REDIS_URL

celery_app = Celery(
    __name__,
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.dashboard.data_loader", "app.dashboard.dash_app"],
)
redis_instance = redis.StrictRedis.from_url(REDIS_URL)
