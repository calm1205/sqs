from typing import TYPE_CHECKING, Any

import boto3
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient


class SQSClientManager:
    def __init__(self) -> None:
        self._mock: Any = None
        self._client: "SQSClient | None" = None

    def start(self) -> None:
        self._mock = mock_aws()
        self._mock.start()
        self._client = boto3.client(
            "sqs",
            region_name="ap-northeast-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )

    def stop(self) -> None:
        if self._mock:
            self._mock.stop()

    def get_client(self) -> "SQSClient":
        if self._client is None:
            raise RuntimeError("SQS client not initialized")
        return self._client


sqs_manager = SQSClientManager()


def get_sqs_client() -> "SQSClient":
    return sqs_manager.get_client()
