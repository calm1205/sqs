import time

from celery import Task

from celery_app import app


@app.task(bind=True)
def process_task(self: Task[[str], dict[str, str]], payload: str) -> dict[str, str]:
    """タスクを処理する。"""
    print(f"Processing task: {payload}")
    time.sleep(1)  # 処理のシミュレーション
    print(f"Completed: {payload}")
    return {"status": "completed", "payload": payload}
