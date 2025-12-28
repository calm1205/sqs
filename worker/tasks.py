import csv
import json
import random
import time
import uuid
from datetime import datetime
from io import StringIO
from typing import Any

from main import app
from models import save_job_result

# サンプルデータ生成用
SAMPLE_PRODUCTS = ["商品A", "商品B", "商品C", "商品D", "商品E"]
SAMPLE_USERS = ["田中", "佐藤", "鈴木", "高橋", "伊藤"]


def generate_sales_data() -> list[dict[str, Any]]:
    """売上データを生成する。"""
    return [
        {
            "id": str(uuid.uuid4())[:8],
            "date": f"2024-01-{random.randint(1, 31):02d}",
            "product": random.choice(SAMPLE_PRODUCTS),
            "quantity": random.randint(1, 100),
            "amount": random.randint(1000, 100000),
        }
        for _ in range(random.randint(50, 200))
    ]


def generate_inventory_data() -> list[dict[str, Any]]:
    """在庫データを生成する。"""
    return [
        {
            "product": product,
            "stock": random.randint(0, 500),
            "warehouse": f"倉庫{random.choice(['A', 'B', 'C'])}",
            "last_updated": datetime.now().isoformat(),
        }
        for product in SAMPLE_PRODUCTS
    ]


def generate_users_data() -> list[dict[str, Any]]:
    """ユーザーデータを生成する。"""
    return [
        {
            "id": i + 1,
            "name": name,
            "email": f"{name.lower()}@example.com",
            "registered_at": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "orders": random.randint(0, 50),
        }
        for i, name in enumerate(SAMPLE_USERS)
    ]


def to_csv(data: list[dict[str, Any]]) -> str:
    """データをCSV文字列に変換する。"""
    if not data:
        return ""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


@app.task(bind=True)
def generate_report(
    self: Any,
    report_type: str,
    output_format: str,
) -> dict[str, Any]:
    """レポートを生成する。"""
    try:
        start_time = time.time()

        # レポート種別に応じてデータ生成
        if report_type == "sales":
            data = generate_sales_data()
        elif report_type == "inventory":
            data = generate_inventory_data()
        elif report_type == "users":
            data = generate_users_data()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # フォーマット変換
        if output_format == "csv":
            content = to_csv(data)
        else:
            content = json.dumps(data, ensure_ascii=False, indent=2)

        elapsed_time = time.time() - start_time

        result = {
            "report_type": report_type,
            "format": output_format,
            "row_count": len(data),
            "content_length": len(content),
            "elapsed_seconds": round(elapsed_time, 2),
            "generated_at": datetime.now().isoformat(),
            "content": content,
        }

        # カスタムテーブルに保存
        save_job_result(
            task_id=self.request.id,
            status="SUCCESS",
            result=result,
        )

        return result

    except Exception as e:
        # 失敗時はFAILUREステータスで保存
        save_job_result(
            task_id=self.request.id,
            status="FAILURE",
            result={"error": str(e)},
        )
        raise
