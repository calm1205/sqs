from pydantic import BaseModel


class TaskRequest(BaseModel):
    payload: str
