# classifier/utils.py
import boto3
import os
from uuid import uuid4

STATE_TO_FOLDER = {
    "не требует ремонта": "no_repair",
    "граффити": "graffiti",
    "плановый ремонт": "scheduled_repair",
    "срочный ремонт": "urgent_repair"
}

def upload_to_s3(file, confirmed_state):
    folder = STATE_TO_FOLDER.get(confirmed_state)
    if not folder:
        raise ValueError("Неизвестная категория")

    ext = os.path.splitext(file.name)[1]
    filename = f"{uuid4()}{ext}"
    key = f"dataset/raw/{folder}/{filename}"

    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    s3.upload_fileobj(file, 'pavilionphotos', key)

    return key  # возвращаем именно путь внутри бакета

def generate_presigned_url(key, expires_in=3600):
    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'pavilionphotos', 'Key': key},
        ExpiresIn=expires_in
    )
    return url
