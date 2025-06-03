from django.urls import path
from .views import TelegramWebhookView
from image_classifier import settings

urlpatterns = [
    path(settings.TELEGRAM_WEBHOOK_PATH.lstrip("/"), TelegramWebhookView.as_view(), name="telegram-webhook"),
]