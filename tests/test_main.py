import json
from unittest.mock import MagicMock

import pytest
import pydantic

from archiver.main import process_archive


def test_bad_payload():
    bad_payload = {"user_email": "john@doe.com"}
    sqs_payload = {'Messages': [{"Body": json.dumps(bad_payload)}]}
    mocked_logger = MagicMock()
    with pytest.raises(pydantic.ValidationError):
        process_archive(None, None, sqs_payload, mocked_logger)
