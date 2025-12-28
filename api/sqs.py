import boto3
from mypy_boto3_sqs import SQSClient

from config import (
    AWS_REGION,
    QUEUE_NAME,
    SQS_ENDPOINT,
)

sqs_client: SQSClient = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
)


def setup_queues() -> None:
    """メインキューをセットアップする。"""
    sqs_client.create_queue(QueueName=QUEUE_NAME)
