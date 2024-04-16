"""Archiver payload validation."""
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MediaSpec(BaseModel):
    """Media definition spec.
    The `source` attribute represents an S3 prefix or a full s3 path.
    The optional `destination` attribute sets the directory and
    file name in the created Zip archive.
    """
    source: str
    destination: Optional[str] = None


class PayloadSpec(BaseModel):
    """Archiver payload spec."""
    files: List[MediaSpec]
    metadata: Optional[Dict[str, Any]] = None


def display_payload_json_schema():
    """Print the json schema manifest of the payload."""
    print(json.dumps(PayloadSpec.model_json_schema(), indent=2))


if __name__ == "__main__":
    display_payload_json_schema()
