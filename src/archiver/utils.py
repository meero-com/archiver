"""Internal functions and classes for the archive creation process."""
from datetime import datetime
import hashlib
from io import BytesIO
from os import path
import typing
from zipfile import ZipFile, ZipInfo
import re

from archiver.config import S3_SOURCE_BUCKET, S3_FILE_PREFIX
from archiver.payload import MediaSpec


def process_file(s3_client, zip_file, file, s3_bucket, s3_key):
    """Fetch the file content and include it in the archive.

    Download the file from S3 and include it in the in-memory ZipFile
    and enforce the directory structure required by the input payload.
    """
    content = s3_client.get_object(
        Bucket=s3_bucket,
        Key=s3_key,
    )
    info = ZipInfo(
        filename=_forge_zip_path(file),
        date_time=tuple(content["LastModified"].timetuple())
    )
    data = zip_file.writestr(info, BytesIO(content["Body"].read()).getbuffer())
    return data


def _forge_zip_path(file: MediaSpec):
    """Return the path of the file used inside the Zip archive.

    This function covers the following scenarios:
    - `destination` has no value: path is `source`;
    - `destination` has no extension: put `source` in `destination` directory;
    - `destination` has an extension: `destination` is file location.

    >>> _forge_zip_path(MediaSpec("abc/def/file.jpg", None))
    'file.jpg'
    >>> _forge_zip_path(MediaSpec("file.jpg", "directory"))
    'directory/file.jpg'
    >>> _forge_zip_path(MediaSpec("file.jpg", "directory/pretty name.jpg"))
    'directory/pretty name.jpg'
    """
    _, filename = path.split(file.source)
    if not file.destination:
        return filename
    _, extension = path.splitext(file.destination)
    if extension:
        return file.destination
    return f"{file.destination}/{filename}"


def create_zip_file() -> typing.Union[ZipFile, BytesIO]:
    """Instantiate a ZipFile in-memory object.

    Return the BytesIO instance in order to easily upload it to
    the S3 Destination bucket once the archive creation is completed.
    """
    file_like_object = BytesIO()
    zip_file = ZipFile(file_like_object, "w")
    return zip_file, file_like_object


def generate_s3_destination_path(creation_date: datetime) -> str:
    """Generate the S3 prefix for the created archive.

    The destination S3 prefix is forged using:
        - a sha256 hash based on the creation_date;
        - a date-based templated zip filename.
    """
    date = creation_date.isoformat()
    prefix_hash = hashlib.new('sha256')
    prefix_hash.update(date.encode('utf-8'))
    digest = prefix_hash.hexdigest()

    file_prefix = S3_FILE_PREFIX
    filename = creation_date.date().isoformat()
    archive_path = f"{digest}/{file_prefix}-{filename}.zip"
    return archive_path

def generate_s3_source_infos_from_payload(file: MediaSpec):
    """Extract s3 source informations from the payload

    The source can be just an s3 key in the S3_SOURCE_BUCKET or a
    full s3 path like `s3://foobar/cool_object.jpg`.

    - Extract the S3 bucket name - Fallback to S3_SOURCE_BUCKET.
    - Extract the S3 key - Fallback to file.source.
    """
    result = re.search(r'^(s3://)?([^/]*)/(.*)$', file.source)
    groups = result.groups() if result is not None else ('', '', '')

    s3_bucket = groups[1] if groups[0] else S3_SOURCE_BUCKET
    s3_key = file.source
    if groups[0] and groups[1]:
        s3_key = groups[2]
    elif groups[1] and groups[2]:
        s3_key = f"{groups[1]}/{groups[2]}"
    return s3_bucket, s3_key
