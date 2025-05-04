# image_classifier/backend/classifier/tasks.py

import os
import tempfile
import boto3
import shutil
from celery import shared_task

from .classifier import maybe_update_model
from .train_model import retrain_if_needed  # Теперь одна главная функция
# не нужно импортировать maybe_update_model отдельно

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = 'pavilionphotos'
ENDPOINT_URL = 'https://storage.yandexcloud.net'

@shared_task
def retrain_model_task():
    print("🚀 Запущена задача переобучения модели!")

    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f"📂 Временная папка для датасета: {tmp_dir}")
        # скачиваем все сырые фото из S3 в tmp_dir/dataset/raw
        dataset_raw = os.path.join(tmp_dir, 'dataset/raw')
        os.makedirs(dataset_raw, exist_ok=True)

        s3 = boto3.client(
            's3',
            endpoint_url=ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        prefixes = [
            "dataset/raw/graffiti/",
            "dataset/raw/no_repair/",
            "dataset/raw/scheduled_repair/",
            "dataset/raw/urgent_repair/"
        ]
        for prefix in prefixes:
            resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
            for obj in resp.get('Contents', []):
                if obj['Key'].endswith('/'):
                    continue
                local_path = os.path.join(tmp_dir, obj['Key'])
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                s3.download_file(BUCKET_NAME, obj['Key'], local_path)

        print("✅ Все файлы из S3 скачаны")

        # переключаем cwd, чтобы retrain_if_needed() писал в правильные папки
        cwd = os.getcwd()
        os.chdir(tmp_dir)
        try:
            retrain_if_needed()
        finally:
            os.chdir(cwd)

    # после успешного дообучения пытаемся обновить модель в памяти Django
    maybe_update_model()

    print("🎉 Задача переобучения завершена!")
