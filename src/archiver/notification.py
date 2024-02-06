"""Scoped module for 3rd party email notification.

Send SQS messages to downstream consumers upon completing an Archive creation.
"""
from dataclasses import asdict, dataclass
from typing import Any, Dict

import json


@dataclass
class ResponseBody:
    """Payload for downtream consumers"""
    metadata: Dict[str, Any]
    substitutions: dict


def send_sqs_message(sqs_client, queue_url: str, message_body: ResponseBody):
    """Send a message to downstream SQS Queue"""
    json_message = json.dumps(asdict(message_body))
    response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=json_message)
    return response
