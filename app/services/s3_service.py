import boto3
import uuid
from app.core.config import settings
from fastapi import UploadFile

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            service_name = "s3",
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            region_name = settings.AWS_REGION
        )

        self.bucket_name = settings.AWS_BUCKET_NAME

    def upload_thumbnail(self, file:UploadFile) -> str:
        extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"

        key = f"project-thumbnail/{filename}"

        self.client.upload_fileobj(
            Fileobj = file.file,
            Bucket = self.bucket_name,
            Key = key,
            ExtraArgs = {
                "ContentType":file.content_type
            }
        )

        url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        
        return url


    
