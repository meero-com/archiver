from archiver.config import is_configuration_valid


def test_valid_config():
    env_subset = {
        'ARCHIVE_BASE_URL': "url",
        'SQS_SOURCE': "sqs-queue",
        'S3_SOURCE_BUCKET': "s3-bucket-source",
        'S3_DESTINATION_BUCKET': "s3-bucket-destination",
        'SQS_DESTINATION': "output-queue",
    }
    assert not any(is_configuration_valid(env_subset)) is True


def test_missing_value_config():
    env_subset = {
        'S3_DESTINATION_BUCKET': "s3-bucket-destination",
    }
    assert not any(is_configuration_valid(env_subset)) is False


def test_empty_value_config():
    env_subset = {
        'ARCHIVE_BASE_URL': "",
        'SQS_SOURCE': "sqs-queue",
        'S3_SOURCE_BUCKET': "s3-bucket-source",
        'S3_DESTINATION_BUCKET': "s3-bucket-destination",
        'SQS_DESTINATION': "output-queue",
    }
    assert not any(is_configuration_valid(env_subset)) is False
