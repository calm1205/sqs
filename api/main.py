import json
import os
from contextlib import asynccontextmanager
from typing import Any

import boto3
from celery import Celery
from fastapi import FastAPI, HTTPException
from mypy_boto3_sqs import SQSClient
from pydantic import BaseModel

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:5000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
QUEUE_NAME = "celery"
DEAD_LETTER_QUEUE_NAME = "celery-dead-letter-queue"
MAX_RECEIVE_COUNT = 3

sqs_client: SQSClient = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """アプリケーションのライフサイクル管理。"""
    setup_queues()
    yield


app = FastAPI(title="API Service", lifespan=lifespan)

celery_app = Celery("worker")
celery_app.conf.update(
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
)


class TaskRequest(BaseModel):
    payload: str


@app.get("/health")
async def health_check() -> dict[str, str]:
    """サービスの稼働状態を確認するヘルスチェック。"""
    return {"status": "healthy"}


@app.post("/tasks")
async def create_task(request: TaskRequest) -> dict[str, str]:
    """Celeryタスクを作成してキューに送信する。"""
    try:
        result = celery_app.send_task("tasks.process_task", args=[request.payload])
        return {
            "message": "Task created",
            "task_id": result.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dead_letter_queue")
async def list_dead_letter_queue_messages() -> dict[str, Any]:
    """Dead Letter Queue内のメッセージ一覧を取得する。"""
    try:
        dead_letter_queue_url = sqs_client.get_queue_url(
            QueueName=DEAD_LETTER_QUEUE_NAME
        )["QueueUrl"]

        # メッセージを取得（最大10件、削除はしない）
        response = sqs_client.receive_message(
            QueueUrl=dead_letter_queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,  # すぐに再取得可能にする
            AttributeNames=["All"],
        )

        messages = response.get("Messages", [])
        return {
            "count": len(messages),
            "messages": [
                {
                    "message_id": msg["MessageId"],
                    "body": msg["Body"],
                    "receive_count": msg.get("Attributes", {}).get(
                        "ApproximateReceiveCount", "0"
                    ),
                }
                for msg in messages
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dead_letter_queue/reprocess")
async def reprocess_dead_letter_queue_messages() -> dict[str, Any]:
    """Dead Letter Queue内の全メッセージをメインキューに再送信する。"""
    try:
        dead_letter_queue_url = sqs_client.get_queue_url(
            QueueName=DEAD_LETTER_QUEUE_NAME
        )["QueueUrl"]

        reprocessed = 0
        while True:
            # Dead Letter Queueからメッセージを取得
            response = sqs_client.receive_message(
                QueueUrl=dead_letter_queue_url,
                MaxNumberOfMessages=10,
                VisibilityTimeout=30,
            )

            messages = response.get("Messages", [])
            if not messages:
                break

            for msg in messages:
                # メッセージ本文からCeleryタスクのペイロードを抽出して再実行
                body = json.loads(msg["Body"])
                task_args = body.get("args", [])
                task_name = body.get("task", "tasks.process_task")

                # タスクを再送信
                celery_app.send_task(task_name, args=task_args)

                # Dead Letter Queueからメッセージを削除
                sqs_client.delete_message(
                    QueueUrl=dead_letter_queue_url,
                    ReceiptHandle=msg["ReceiptHandle"],
                )
                reprocessed += 1

        return {
            "message": "Dead letter queue messages reprocessed",
            "reprocessed_count": reprocessed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
