import json
from unittest.mock import MagicMock

def test_valid_payload_sqs(mock_aws, monkeypatch):
    import archiver.main
    import archiver.logs
    logger = archiver.logs.bootstrap_logging('e2e', True, True)
    body = {
      "files": [
        {
          "source": "source.jpg",
          "destination": "album_1"
        },
      ],
      "sendgrid_template_id": "d-xxxxxx",
      "user_email": "customer@e2e.test"
    }
    payload = {
        'Messages': [
            {
                'messageId': 'dummy-message-id',
                'eventSource': 'aws:sqs',
                'ReceiptHandle': 'dummy-handle',
                'Body': json.dumps(body),
                'MessageAttributes': {
                    'Correlation-Id': {
                        'StringValue': 'Root=some-correlation-id',
                        'DataType': 'String',
                     },
                },
            }
        ],
    }
    sqs_client, s3_client = archiver.main.bootstrap_archiver(logger)
    monkeypatch.setattr(sqs_client, 'delete_message', lambda *_, **__: True)
    s3_key = archiver.main.process_archive(s3_client, sqs_client, payload, logger)

    s3_bucket = 'zip-storage'
    response = s3_client.head_object(
        Bucket=s3_bucket,
        Key=s3_key,
    )
    assert response['ContentLength'] > 0
    s3_client.delete_object(
        Bucket=s3_bucket,
        Key=s3_key,
    )

    message = sqs_client.receive_message(
        QueueUrl='http://localhost:4566/000000000000/output-queue',
    )
    records = message.get('Messages', [])
    assert len(records) >= 1
    sqs_client.delete_message(
        QueueUrl='http://localhost:4566/000000000000/output-queue',
        ReceiptHandle=records[0]['ReceiptHandle'],
    )
