from app.services.s3_service import S3Service
from types import SimpleNamespace

s3_service = S3Service()

def test_s3_client_create():

    print("S3 Client 생성 성공")
    print(s3_service.client)

test_s3_client_create()

def test_file_upload():
    with open("tests/assets/test.jpg", "rb") as f:
        file = SimpleNamespace(
            file = f,
            filename = "test.jpg",
            content_type = "image/jpeg"
        )

        result = s3_service.upload_thumbnail(file)

        print(result)

test_file_upload()