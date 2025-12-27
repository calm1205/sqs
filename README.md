# Local SQS Service

motoを使用したローカルSQSサービス。FastAPIで実装。

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

## エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/health` | ヘルスチェック |
| POST | `/queues` | キュー作成 |
| GET | `/queues` | キュー一覧 |
| DELETE | `/queues?queue_url=...` | キュー削除 |
| POST | `/messages` | メッセージ送信 |
| GET | `/messages?queue_url=...` | メッセージ受信 |
| DELETE | `/messages` | メッセージ削除 |
| GET | `/queues/attributes?queue_url=...` | キュー属性取得 |

## 使用例

```bash
# キュー作成
curl -X POST http://localhost:8000/queues \
  -H "Content-Type: application/json" \
  -d '{"queue_name": "test-queue"}'

# メッセージ送信
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"queue_url": "http://sqs.ap-northeast-1.amazonaws.com/123456789012/test-queue", "message_body": "Hello SQS!"}'

# メッセージ受信
curl "http://localhost:8000/messages?queue_url=http://sqs.ap-northeast-1.amazonaws.com/123456789012/test-queue"
```
