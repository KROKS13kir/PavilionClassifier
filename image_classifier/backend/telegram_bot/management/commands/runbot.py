from django.core.management.base import BaseCommand
from telegram_bot.bot import build_app
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **options):
        app = build_app()
        if settings.TELEGRAM_USE_WEBHOOK:
            # TELEGRAM_WEBHOOK_PATH = "/telegram/webhook/"
            url_path = settings.TELEGRAM_WEBHOOK_PATH.lstrip("/")  # -> "telegram/webhook/"
            app.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv("PORT", 8443)),
                url_path=url_path,
                webhook_url=f"{settings.TELEGRAM_WEBHOOK_HOST}{settings.TELEGRAM_WEBHOOK_PATH}"
            )
        else:
            app.run_polling()