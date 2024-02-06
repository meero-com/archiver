import datetime

import pytest


@pytest.mark.parametrize(
    'source,destination,expected_path',
    [
        ("abc/def/file.jpg", None, "file.jpg"),
        ("file.jpg", "destination", "destination/file.jpg"),
        ("file.jpg", "destination/Photo 1.jpg", "destination/Photo 1.jpg"),
        ("file.jpg", "Photo 1.jpg", "Photo 1.jpg"),
        ("file.jpg", "", "file.jpg"),
    ]
)
def test_forge_zip_path(source, destination, expected_path):
    import archiver.utils
    from archiver.payload import MediaSpec
    media_spec = MediaSpec(source=source, destination=destination)
    assert archiver.utils._forge_zip_path(media_spec) == expected_path


def test_generate_destination_path():
    import archiver.utils

    date = datetime.datetime.now()
    actual_date = date.date().isoformat()
    generated_path = archiver.utils.generate_s3_destination_path(date)
    assert generated_path.endswith(f'meero-download-{actual_date}.zip')

@pytest.mark.parametrize(
    'source,destination',
    [
        ("abc/def/file.jpg", "Album / Photo")
    ]
)
def test_generate_s3_source_with_no_s3_uri(source, destination):
    from archiver.utils import generate_s3_source_infos_from_payload
    from archiver.payload import MediaSpec
    from archiver.config import S3_SOURCE_BUCKET

    media_spec = MediaSpec(source=source, destination=destination)
    s3_bucket, s3_key = generate_s3_source_infos_from_payload(media_spec)
    assert s3_bucket == S3_SOURCE_BUCKET
    assert s3_key == media_spec.source

@pytest.mark.parametrize(
    'source,destination',
    [
        ("s3://bucket_name/abc/def/file.jpg", "Album / Photo")
    ]
)
def test_generate_s3_source_with_s3_uri(source, destination):
    from archiver.utils import generate_s3_source_infos_from_payload
    from archiver.payload import MediaSpec
    from archiver.config import S3_SOURCE_BUCKET

    media_spec = MediaSpec(source=source, destination=destination)
    s3_bucket, s3_key = generate_s3_source_infos_from_payload(media_spec)
    assert s3_bucket == "bucket_name"
    assert s3_key == "abc/def/file.jpg"
