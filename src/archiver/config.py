import os


ARCHIVE_BASE_URL = os.environ.get("ARCHIVE_BASE_URL", "")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")
DEBUG = int(os.environ.get('DEBUG', "0"))
DEV_MODE = int(os.environ.get('DEV_MODE', "0"))

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@meero.com")
SENDER_NAME = os.environ.get("SENDER_NAME", "Meero")

SQS_SOURCE = os.environ.get('SQS_SOURCE_QUEUE')
S3_SOURCE_BUCKET = os.environ.get('S3_SOURCE_BUCKET')
S3_DESTINATION_BUCKET = os.environ.get('S3_DESTINATION_BUCKET')

SQS_DESTINATION = os.environ.get('SQS_DESTINATION_QUEUE')


def is_configuration_valid(config: dict) -> dict:
    """Ensure required variables are set properly.

    Return the list of errors if any."""
    required = {
        'ARCHIVE_BASE_URL',
        'SQS_SOURCE',
        'S3_SOURCE_BUCKET',
        'S3_DESTINATION_BUCKET',
        'SQS_DESTINATION',
    }
    errors = {}
    for key in required:
        if key not in config:
            errors[key] = "missing value"
        if not config.get(key):
            errors[key] = "empty value"
    return errors
