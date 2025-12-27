from fastapi import APIRouter, HTTPException

from app.dependencies import get_sqs_client
from app.schemas import CreateQueueRequest

router = APIRouter(prefix="/queues", tags=["queues"])


@router.post("")
async def create_queue(request: CreateQueueRequest):
    try:
        response = get_sqs_client().create_queue(QueueName=request.queue_name)
        return {"queue_url": response["QueueUrl"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_queues():
    try:
        response = get_sqs_client().list_queues()
        return {"queue_urls": response.get("QueueUrls", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("")
async def delete_queue(queue_url: str):
    try:
        get_sqs_client().delete_queue(QueueUrl=queue_url)
        return {"message": "Queue deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attributes")
async def get_queue_attributes(queue_url: str):
    try:
        response = get_sqs_client().get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["All"],
        )
        return {"attributes": response.get("Attributes", {})}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
