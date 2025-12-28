import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

from celery_client import celery_app
from schemas import TaskRequest
from sqs import get_dead_letter_queue_url, setup_queues, sqs_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """アプリケーションのライフサイクル管理。"""
    setup_queues()
    yield


app = FastAPI(title="API Service", lifespan=lifespan)


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


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """タスクの進捗状況を取得する。

    Note: Result backendが未設定の場合、ステータスは常にPENDINGとなる。
    """
    result = celery_app.AsyncResult(task_id)
    response: dict[str, Any] = {
        "task_id": task_id,
        "status": result.status,
    }
    try:
        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                response["error"] = str(result.result)
    except AttributeError:
        # Result backendが無効な場合
        response["note"] = "Result backend is not configured"
    return response


@app.get("/dead_letter_queue")
async def list_dead_letter_queue_messages() -> dict[str, Any]:
    """Dead Letter Queue内のメッセージ一覧を取得する。"""
    try:
        dead_letter_queue_url = get_dead_letter_queue_url()

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
        dead_letter_queue_url = get_dead_letter_queue_url()

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
