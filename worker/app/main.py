import os
import time

import boto3

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:8000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
QUEUE_NAME = os.getenv("QUEUE_NAME", "default-queue")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

sqs_client = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
)


def get_queue_url() -> str | None:
    """キューURLを取得する。存在しない場合はNoneを返す。"""
    try:
        response = sqs_client.get_queue_url(QueueName=QUEUE_NAME)
        return response["QueueUrl"]
    except sqs_client.exceptions.QueueDoesNotExist:
        return None


def process_message(body: str) -> None:
    """メッセージを処理する。"""
    print(f"Processing message: {body}")
    # ここに実際の処理を実装
    time.sleep(1)  # 処理のシミュレーション
    print(f"Completed: {body}")


def poll_messages() -> None:
    """キューからメッセージをポーリングして処理する。"""
    queue_url = get_queue_url()
    if queue_url is None:
        print(f"Queue '{QUEUE_NAME}' does not exist. Waiting...")
        return

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,
    )

    messages = response.get("Messages", [])
    if not messages:
        print("No messages received")
        return

    for msg in messages:
        try:
            process_message(msg["Body"])
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )
            print(f"Deleted message: {msg['MessageId']}")
        except Exception as e:
            print(f"Error processing message: {e}")


def main() -> None:
    """Workerのメインループ。"""
    print(f"Worker started. Polling queue: {QUEUE_NAME}")
    while True:
        try:
            poll_messages()
        except Exception as e:
            print(f"Error polling: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
