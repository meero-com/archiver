"""Archiver main high level processing loop and bootstrapping.

Configuration operates through environment variables exclusively (see `archiver.config`).

The archiver has the following flow:
    - Instantiate logger.
    - Instantiate boto clients (S3, SQS).
    - Start polling message (infinite loop).

Each processed message will trigger the following processing:
    - Create an in-memory file-like object based ZipFile.
    - Download each media and write it to the archive.
    - Upload the archive to the S3_DESTINATION_BUCKET.
    - Send SQS message to downstream consumers.
"""
import os
from datetime import datetime
import json

import boto3
from pydantic import ValidationError

from archiver.config import (
    ARCHIVE_BASE_URL,
    AWS_ENDPOINT_URL,
    DEBUG,
    DEV_MODE,
    SQS_DESTINATION,
    SQS_SOURCE,
    S3_DESTINATION_BUCKET,
    is_configuration_valid,
)
from archiver.notification import (
    ResponseBody,
    send_sqs_message,
)
from archiver.utils import (
    create_zip_file,
    generate_s3_destination_path,
    process_file,
    generate_s3_source_infos_from_payload
)
from archiver.payload import MediaSpec, PayloadSpec
from archiver.logs import bootstrap_logging


POLLING_WAIT_TIME = 20  # seconds


def poll_sqs(sqs_client, queue_url, logger):
    """Retrieve a message from the source SQS Queue.

    Interacting with the WaitTimeSeconds argument of the receive_message
    function allows to balance between cost efficiency and performances.
    """
    while True:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=POLLING_WAIT_TIME,
        )
        messages = response.get('Messages', [])
        if len(messages) > 0:
            yield response
            continue
        logger.debug("no message from SQS, going back to polling")


def process_archive(s3_client, sqs_client, sqs_response, logger):
    """Download files from S3, create and upload zip archive to S3."""
    message = sqs_response['Messages'][0]
    content = json.loads(message["Body"])

    try:
        PayloadSpec.model_validate(content)
    except ValidationError as error:
        logger.error(
            'payload does not match expected format %s content=%s',
            error,
            content,
        )
        raise

    logger.debug(
        "processing watermark request",
        payload=content,
    )
    archive_s3_path = generate_s3_destination_path(datetime.now())

    source_files = [MediaSpec(**item) for item in content['files']]

    logger.info(
        "processing message for archive %s",
        archive_s3_path,
        extra={
            'archive': {
                'file_count': len(source_files),
            },
        },
    )
    # Create archive
    zip_file, file_handle = create_zip_file()
    for item in source_files:
        s3_bucket, s3_key = generate_s3_source_infos_from_payload(item)
        logger.debug(
            "extracting s3 source infos before processing - bucket : %s - key : %s",
            s3_bucket,
            s3_key
        )
        process_file(s3_client, zip_file, item, s3_bucket, s3_key)

    zip_file.close()
    # Upload archive to S3
    file_handle.seek(0)  # rewind to start of the file
    s3_client.upload_fileobj(file_handle, S3_DESTINATION_BUCKET, archive_s3_path)

    logger.info(
        "successfully uploaded archive to s3://%s/%s",
        S3_DESTINATION_BUCKET,
        archive_s3_path,
        extra={'archive': {'file_count': len(source_files)}},
    )

    archive_url = f"{ARCHIVE_BASE_URL}/{archive_s3_path}"
    if SQS_DESTINATION is not None:
        message_body = ResponseBody(
            metadata=content.get('metadata'),
            substitutions={'archiver_URL': archive_url},
        )

        response = send_sqs_message(
            sqs_client=sqs_client,
            queue_url=SQS_DESTINATION,
            message_body=message_body,
        )

        logger.info(
            "Message successfully sent to queue %s MessageId=%s",
            SQS_DESTINATION,
            response['MessageId'],
        )
    else:
        logger.info('skipping sqs message because SQS_DESTINATION is not set')
    # Cleanup / acknowledge processing
    sqs_client.delete_message(
        QueueUrl=SQS_SOURCE,
        ReceiptHandle=message['ReceiptHandle'],
    )
    logger.info(
        "done processing request with template_id=%s",
        content['sendgrid_template_id'],
    )
    return archive_s3_path


def bootstrap_archiver(logger):
    """Validate configuration and instantiate boto3 client services."""
    if not is_configuration_valid(os.environ):
        raise ValueError('configuration is invalid')
    if AWS_ENDPOINT_URL is not None:
        logger.info('using AWS_ENDPOINT_URL=%s', AWS_ENDPOINT_URL)
    sqs_client = boto3.client('sqs', endpoint_url=AWS_ENDPOINT_URL)
    s3_client = boto3.client('s3', endpoint_url=AWS_ENDPOINT_URL)
    return sqs_client, s3_client


def main():
    """Archiver entrypoint."""
    debug_mode, dev_mode = DEBUG == 1, DEV_MODE == 1
    logger = bootstrap_logging('archiver', debug_mode, dev_mode)
    logger.info("bootstrap archiver boto clients")
    sqs_client, s3_client = bootstrap_archiver(logger)
    logger.debug("instantiated boto clients")

    logger.info(f"start polling messages from {SQS_SOURCE}")
    for sqs_response in poll_sqs(sqs_client, SQS_SOURCE, logger):
        try:
            process_archive(s3_client, sqs_client, sqs_response, logger)
        except Exception as err:
            logger.error(
                "could not process message %s: %r",
                type(err),
                err,
            )


if __name__ == "__main__":
    main()
