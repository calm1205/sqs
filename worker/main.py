import os
from urllib.parse import urlparse

import boto3
from celery import Celery

from models import init_db

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:4566")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
QUEUE_NAME = os.getenv("QUEUE_NAME", "celery")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "db+sqlite:///data/celery_results.db")

parsed_endpoint = urlparse(SQS_ENDPOINT)
broker_host = parsed_endpoint.hostname or "sqs"
broker_port = f":{parsed_endpoint.port}" if parsed_endpoint.port else ""
is_secure = parsed_endpoint.scheme == "https"
broker_url = f"sqs://@{broker_host}{broker_port}"

sqs_client = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
)


def ensure_queues() -> str:
    """LocalStack上にキューを用意し、URLを返す。"""
    queue_response = sqs_client.create_queue(QueueName=QUEUE_NAME)
    return queue_response["QueueUrl"]


QUEUE_URL = ensure_queues()

# カスタムテーブルの初期化
init_db()

app = Celery("worker")

app.conf.update(
    broker_url=broker_url,
    broker_transport_options={
        "region": AWS_REGION,
        "is_secure": is_secure,
        "predefined_queues": {
            "celery": {
                "url": QUEUE_URL,
            }
        },
    },
    result_backend=RESULT_BACKEND,
    task_default_queue="celery",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    imports=["tasks"],
)
