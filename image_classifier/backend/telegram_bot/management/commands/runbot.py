from django.core.management.base import BaseCommand
from telegram_bot.bot import build_app
from django.conf import settings

class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **options):
        app = build_app()
        if settings.TELEGRAM_USE_WEBHOOK:
            app.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv("PORT", 8443)),
                webhook_url=f"{settings.TELEGRAM_WEBHOOK_HOST}{settings.TELEGRAM_WEBHOOK_PATH}"
            )
        else:
            app.run_polling()