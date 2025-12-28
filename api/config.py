import os
from urllib.parse import urlparse

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:4566")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "000000000000")

parsed_endpoint = urlparse(SQS_ENDPOINT)
BROKER_HOST = parsed_endpoint.hostname or "sqs"
BROKER_PORT = f":{parsed_endpoint.port}" if parsed_endpoint.port else ""
BROKER_URL = f"sqs://@{BROKER_HOST}{BROKER_PORT}"
IS_SECURE = parsed_endpoint.scheme == "https"

QUEUE_NAME = "celery"
DEAD_LETTER_QUEUE_NAME = "celery-dead-letter-queue"
MAX_RECEIVE_COUNT = 3
