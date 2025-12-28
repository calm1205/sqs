from celery import Celery
from config import (
    AWS_ACCOUNT_ID,
    AWS_REGION,
    BROKER_URL,
    IS_SECURE,
    RESULT_BACKEND,
    SQS_ENDPOINT,
)

celery_app = Celery("worker")
celery_app.conf.update(
    broker_url=BROKER_URL,
    broker_transport_options={
        "region": AWS_REGION,
        "is_secure": IS_SECURE,
        "predefined_queues": {
            "celery": {
                "url": f"{SQS_ENDPOINT}/{AWS_ACCOUNT_ID}/celery",
            }
        },
    },
    result_backend=RESULT_BACKEND,
    task_default_queue="celery",
    result_serializer="json",
    accept_content=["json"],
)
