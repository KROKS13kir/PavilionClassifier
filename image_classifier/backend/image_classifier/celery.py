import os
from celery import Celery

# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_classifier.settings')

# Создаём объект Celery
app = Celery('image_classifier')

# Загружаем настройки Celery из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически искать задачи в приложениях
app.autodiscover_tasks()
