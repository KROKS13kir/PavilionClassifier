from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ImageUpload
import boto3
import os

STATE_TO_FOLDER = {
    "не требует ремонта": "no_repair",
    "граффити": "graffiti",
    "плановый ремонт": "scheduled_repair",
    "срочный ремонт": "urgent_repair"
}

@receiver(post_save, sender=ImageUpload)
def upload_to_s3_and_check_retrain(sender, instance, created, **kwargs):
    if not created or not instance.image_url:
        return

    folder_name = STATE_TO_FOLDER.get(instance.confirmed_state)
    if not folder_name:
        print("⚠️ Неизвестная категория")
        return

    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    bucket = 'pavilionphotos'

    # Проверяем количество файлов
    retrain_needed = False
    for folder in STATE_TO_FOLDER.values():
        response = s3.list_objects_v2(Bucket=bucket, Prefix=f'dataset/raw/{folder}/')
        count = len(response.get('Contents', []))
        if count >= 150 and (count - 100) % 50 == 0:
            retrain_needed = True

    if retrain_needed:
        print("🚀 Условие выполнено — отправляем задачу на переобучение Celery!")
        from .tasks import retrain_model_task
        retrain_model_task.delay()
