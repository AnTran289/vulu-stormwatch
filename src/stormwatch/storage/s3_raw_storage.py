import json
from datetime import UTC, datetime
from typing import Any

import boto3
from botocore.client import BaseClient


class S3RawStorage:
    def __init__(
        self,
        bucket_name: str,
        s3_client: BaseClient | None = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.s3_client = s3_client or boto3.client("s3")

    def save_json(
        self,
        source: str,
        data: dict[str, Any] | list[Any],
    ) -> str:
        extracted_at = datetime.now(UTC)

        filename = extracted_at.strftime(
            "%Y%m%d_%H%M%S_%f.json"
        )

        key = (
            f"{source}/"
            f"{extracted_at:%Y/%m/%d}/"
            f"{filename}"
        )

        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            ContentType="application/json",
        )

        return f"s3://{self.bucket_name}/{key}"
