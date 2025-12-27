from fastapi import APIRouter, HTTPException

from app.dependencies import get_sqs_client
from app.schemas import DeleteMessageRequest, SendMessageRequest

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("")
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


@router.get("")
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


@router.delete("")
async def delete_message(request: DeleteMessageRequest):
    try:
        get_sqs_client().delete_message(
            QueueUrl=request.queue_url,
            ReceiptHandle=request.receipt_handle,
        )
        return {"message": "Message deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
