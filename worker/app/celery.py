import os

from celery import Celery

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://localhost:5000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

app = Celery("worker")

app.conf.update(
    broker_url="sqs://@",
    broker_transport_options={
        "region": AWS_REGION,
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

app.autodiscover_tasks(["app"])
