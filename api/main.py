from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

from celery_client import celery_app
from models import get_job_result
from schemas import ReportRequest
from sqs import setup_queues


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


@app.post("/reports")
async def create_report(request: ReportRequest) -> dict[str, str]:
    """レポート生成タスクを作成してキューに送信する。"""
    try:
        result = celery_app.send_task(
            "tasks.generate_report",
            args=[request.report_type.value, request.format.value],
        )
        return {
            "message": "Report generation started",
            "task_id": result.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{task_id}")
async def get_report_status(task_id: str) -> dict[str, Any]:
    """レポート生成タスクの進捗状況を取得する（カスタムテーブルから）。"""
    job = get_job_result(task_id)
    if job:
        return {
            "task_id": job.task_id,
            "status": job.status,
            "result": job.result,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }

    # カスタムテーブルにない場合はCeleryのステータスを確認
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
    }
