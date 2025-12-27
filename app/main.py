from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import boto3
from fastapi import FastAPI, HTTPException
from moto import mock_aws
from pydantic import BaseModel

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient


class CreateQueueRequest(BaseModel):
    queue_name: str


class SendMessageRequest(BaseModel):
    queue_url: str
    message_body: str
    delay_seconds: int = 0


class ReceiveMessageRequest(BaseModel):
    queue_url: str
    max_number_of_messages: int = 1
    wait_time_seconds: int = 0


class DeleteMessageRequest(BaseModel):
    queue_url: str
    receipt_handle: str


# Global moto mock and SQS client
mock: Any = None
sqs_client: "SQSClient | None" = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mock, sqs_client
    mock = mock_aws()
    mock.start()
    sqs_client = boto3.client(
        "sqs",
        region_name="ap-northeast-1",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )
    yield
    mock.stop()


app = FastAPI(title="Local SQS Service with Moto", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def get_sqs_client() -> "SQSClient":
    if sqs_client is None:
        raise RuntimeError("SQS client not initialized")
    return sqs_client


@app.post("/queues")
async def create_queue(request: CreateQueueRequest):
    try:
        response = get_sqs_client().create_queue(QueueName=request.queue_name)
        return {"queue_url": response["QueueUrl"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/queues")
async def list_queues():
    try:
        response = get_sqs_client().list_queues()
        return {"queue_urls": response.get("QueueUrls", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/queues")
async def delete_queue(queue_url: str):
    try:
        get_sqs_client().delete_queue(QueueUrl=queue_url)
        return {"message": "Queue deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/messages")
async def send_message(request: SendMessageRequest):
    try:
        response = get_sqs_client().send_message(
            QueueUrl=request.queue_url,
            MessageBody=request.message_body,
            DelaySeconds=request.delay_seconds,
        )
        return {
            "message_id": response["MessageId"],
            "md5_of_message_body": response["MD5OfMessageBody"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/messages")
async def receive_messages(
    queue_url: str,
    max_number_of_messages: int = 1,
    wait_time_seconds: int = 0,
):
    try:
        response = get_sqs_client().receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
        )
        messages = response.get("Messages", [])
        return {
            "messages": [
                {
                    "message_id": msg["MessageId"],
                    "receipt_handle": msg["ReceiptHandle"],
                    "body": msg["Body"],
                    "md5_of_body": msg["MD5OfBody"],
                }
                for msg in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/messages")
async def delete_message(request: DeleteMessageRequest):
    try:
        get_sqs_client().delete_message(
            QueueUrl=request.queue_url,
            ReceiptHandle=request.receipt_handle,
        )
        return {"message": "Message deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/queues/attributes")
async def get_queue_attributes(queue_url: str):
    try:
        response = get_sqs_client().get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["All"],
        )
        return {"attributes": response.get("Attributes", {})}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
