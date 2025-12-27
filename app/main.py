from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.dependencies import sqs_manager
from app.routers import messages, queues


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    sqs_manager.start()
    yield
    sqs_manager.stop()


app = FastAPI(title="Local SQS Service with Moto", lifespan=lifespan)

app.include_router(queues.router)
app.include_router(messages.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
