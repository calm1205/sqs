import os

import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:8000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

app = FastAPI(title="API Service")

sqs_client = boto3.client(
    "sqs",
    endpoint_url=SQS_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
)


class TaskRequest(BaseModel):
    task_type: str
    payload: str


@app.get("/health")
async def health_check():
    """サービスの稼働状態を確認するヘルスチェック。"""
    return {"status": "healthy"}


@app.post("/tasks")
async def create_task(request: TaskRequest):
    """タスクを作成してSQSキューに送信する。"""
    try:
        # キューURLを取得（なければ作成）
        queue_name = f"{request.task_type}-queue"
        try:
            response = sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response["QueueUrl"]
        except sqs_client.exceptions.QueueDoesNotExist:
            response = sqs_client.create_queue(QueueName=queue_name)
            queue_url = response["QueueUrl"]

        # メッセージ送信
        result = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=request.payload,
        )
        return {
            "message": "Task created",
            "message_id": result["MessageId"],
            "queue": queue_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
