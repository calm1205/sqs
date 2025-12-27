from pydantic import BaseModel


class CreateQueueRequest(BaseModel):
    queue_name: str


class SendMessageRequest(BaseModel):
    queue_url: str
    message_body: str
    delay_seconds: int = 0


class DeleteMessageRequest(BaseModel):
    queue_url: str
    receipt_handle: str
