import json
import os
from urllib.parse import urlparse

import boto3
from celery import Celery

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:4566")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")
QUEUE_NAME = os.getenv("QUEUE_NAME", "celery")
DEAD_LETTER_QUEUE_NAME = os.getenv("DEAD_LETTER_QUEUE_NAME", "celery-dead-letter-queue")
MAX_RECEIVE_COUNT = int(os.getenv("MAX_RECEIVE_COUNT", "3"))

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
    """LocalStack上にキュー（DLQ含む）を用意し、URLを返す。"""
    dead_letter_queue_response = sqs_client.create_queue(
        QueueName=DEAD_LETTER_QUEUE_NAME
    )
    dead_letter_queue_url = dead_letter_queue_response["QueueUrl"]
    dead_letter_queue_attrs = sqs_client.get_queue_attributes(
        QueueUrl=dead_letter_queue_url,
        AttributeNames=["QueueArn"],
    )
    dead_letter_queue_arn = dead_letter_queue_attrs["Attributes"]["QueueArn"]

    queue_response = sqs_client.create_queue(
        QueueName=QUEUE_NAME,
        Attributes={
            "RedrivePolicy": json.dumps(
                {
                    "deadLetterTargetArn": dead_letter_queue_arn,
                    "maxReceiveCount": str(MAX_RECEIVE_COUNT),
                }
            )
        },
    )
    return queue_response["QueueUrl"]


QUEUE_URL = ensure_queues()

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
    task_default_queue="celery",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
