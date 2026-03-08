"""
Celery application configured with Redis broker and backend.
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "lead_generation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.pipeline"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="lead_generation",
    task_routes={
        "app.tasks.pipeline.task_generate_grids": {"queue": "grid"},
        "app.tasks.pipeline.task_search_maps": {"queue": "search"},
        "app.tasks.pipeline.task_fetch_details": {"queue": "details"},
        "app.tasks.pipeline.task_crawl_website": {"queue": "crawl"},
        "app.tasks.pipeline.task_extract_emails": {"queue": "email"},
    },
)
