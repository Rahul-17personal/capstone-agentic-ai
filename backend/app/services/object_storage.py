import boto3
from app.config import settings


def s3_enabled() -> bool:
    return bool(settings.AWS_S3_BUCKET)


def upload_bytes(data: bytes, key: str, content_type: str) -> str:
    if not s3_enabled():
        raise RuntimeError("S3 storage is not configured. Set AWS_S3_BUCKET and AWS_REGION.")
    client = boto3.client("s3", region_name=settings.AWS_REGION)
    client.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
        ServerSideEncryption="AES256",
    )
    return key


def create_download_url(key: str, expires_seconds: int = 600) -> str:
    if not s3_enabled():
        raise RuntimeError("S3 storage is not configured.")
    client = boto3.client("s3", region_name=settings.AWS_REGION)
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
        ExpiresIn=expires_seconds,
    )
