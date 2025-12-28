import json

import boto3
from mypy_boto3_sqs import SQSClient

from config import (
    AWS_REGION,
    DEAD_LETTER_QUEUE_NAME,
    MAX_RECEIVE_COUNT,
    QUEUE_NAME,
    SQS_ENDPOINT,
)

sqs_client: SQSClient = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
)


def setup_queues() -> None:
    """メインキューとDead Letter Queueをセットアップする。"""
    # Dead Letter Queueを作成
    dead_letter_queue_response = sqs_client.create_queue(
        QueueName=DEAD_LETTER_QUEUE_NAME
    )
    dead_letter_queue_url = dead_letter_queue_response["QueueUrl"]

    # Dead Letter QueueのARNを取得
    dead_letter_queue_attrs = sqs_client.get_queue_attributes(
        QueueUrl=dead_letter_queue_url, AttributeNames=["QueueArn"]
    )
    dead_letter_queue_arn = dead_letter_queue_attrs["Attributes"]["QueueArn"]

    # メインキューをRedrive Policy付きで作成
    sqs_client.create_queue(
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


def get_dead_letter_queue_url() -> str:
    """Dead Letter QueueのURLを取得する。"""
    return sqs_client.get_queue_url(QueueName=DEAD_LETTER_QUEUE_NAME)["QueueUrl"]
