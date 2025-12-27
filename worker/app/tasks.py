import time
from typing import Any

from app.celery import app


@app.task(bind=True)  # type: ignore[untyped-decorator]
def process_task(self: Any, payload: str) -> dict[str, str]:
    """タスクを処理する。"""
    print(f"Processing task: {payload}")
    time.sleep(1)  # 処理のシミュレーション
    print(f"Completed: {payload}")
    return {"status": "completed", "payload": payload}
