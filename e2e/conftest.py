import os
import pytest


@pytest.fixture
def mock_aws(monkeypatch):
    monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost.localstack.cloud:4566")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "mock")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "mock")
    monkeypatch.setenv("S3_SOURCE_BUCKET", "source-images")
    monkeypatch.setenv("S3_DESTINATION_BUCKET", "zip-storage")
    monkeypatch.setenv("SQS_SOURCE_QUEUE", "http://localhost:4566/000000000000/input-queue")
    monkeypatch.setenv("SQS_DESTINATION_QUEUE", "http://localhost:4566/000000000000/output-queue")
