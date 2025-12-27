import os

from celery import Celery
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SQS_ENDPOINT = os.getenv("SQS_ENDPOINT", "http://sqs:5000")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

app = FastAPI(title="API Service")

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
        result = celery_app.send_task("app.tasks.process_task", args=[request.payload])
        return {
            "message": "Task created",
            "task_id": result.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
