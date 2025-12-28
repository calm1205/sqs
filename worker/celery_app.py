import os

from celery import Celery
from celery.app.task import Task

# celery-typesでジェネリック型を使用するためのmonkey patch
Task.__class_getitem__ = classmethod(  # type: ignore[attr-defined]
    lambda cls, *args, **kwargs: cls
)

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://localhost:5000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

app = Celery("worker")

app.conf.update(
    broker_url="sqs://@",
    broker_transport_options={
        "region": AWS_REGION,
        "is_secure": False,
        "endpoint_url": SQS_ENDPOINT,
        "aws_access_key_id": "testing",
        "aws_secret_access_key": "testing",
        "predefined_queues": {
            "celery": {
                "url": f"{SQS_ENDPOINT}/000000000000/celery",
            }
        },
    },
    task_default_queue="celery",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# タスクを自動検出
import tasks  # noqa: E402, F401
