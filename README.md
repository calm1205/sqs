# Local SQS Service

motoを使用したローカルSQSサービス。Celery + SQSブローカーによる非同期タスク処理。

## アーキテクチャ

```
┌─────────┐     ┌─────────────┐     ┌────────┐
│   API   │────▶│ SQS (moto)  │◀────│ Worker │
│ FastAPI │     │ moto_server │     │ Celery │
└─────────┘     └─────────────┘     └────────┘
     │                │
     │                ▼
     │         ┌─────────────────────┐
     └────────▶│ Dead Letter Queue   │
               └─────────────────────┘
```

## 必要条件

- Docker
- uv (ローカル開発時)

## 起動方法

```bash
docker compose watch
```

## ローカル開発

```bash
uv venv
uv sync
make lint
```

## サービス構成

| サービス | ポート | 説明 |
|----------|--------|------|
| api | 8000 | FastAPI アプリケーション |
| worker | - | Celery ワーカー |
| sqs | 5001 | moto_server (SQSモック) |

## エンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/health` | ヘルスチェック |
| POST | `/tasks` | タスク作成 |
| GET | `/dead_letter_queue` | Dead Letter Queue メッセージ一覧 |
| POST | `/dead_letter_queue/reprocess` | Dead Letter Queue メッセージ再処理 |

## 使用例

```bash
# タスク作成
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"payload": "Hello Celery!"}'

# Dead Letter Queue 確認
curl http://localhost:8000/dead_letter_queue

# Dead Letter Queue 再処理
curl -X POST http://localhost:8000/dead_letter_queue/reprocess
```

## 環境変数

`.env` ファイルで設定:

| 変数名 | デフォルト値 | 説明 |
|--------|--------------|------|
| AWS_REGION | ap-northeast-1 | AWSリージョン |
| SQS_ENDPOINT | http://sqs:5000 | SQSエンドポイント |
