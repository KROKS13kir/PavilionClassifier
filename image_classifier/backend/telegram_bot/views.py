import json

from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest

from telegram import Update

import asyncio

from telegram_bot.bot import build_app


class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        data = request.body
        update = Update.de_json(json.loads(data), bot=build_app().bot)
        asyncio.run(build_app().process_update(update))
        return JsonResponse({"status": "ok"})

