import asyncio
import telegram
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from classifier.models import RepairOrder

@receiver(post_save, sender=RepairOrder)
def notify_employee_on_order_change(sender, instance, created, **kwargs):
    if not instance.employee or not instance.employee.telegram_chat_id:
        return

    chat_id = instance.employee.telegram_chat_id
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)

    text = (
        f"🔧 Наряд #{instance.id} обновлён!\n"
        f"📍 Остановка: {instance.pavilion.stop_name}\n"
        f"🗓 Дата: {instance.scheduled_for}\n"
        f"📌 Статус: {instance.get_status_display()}"
    )
    if created:
        text = "🆕 *Создан новый наряд!*\n" + text

    async def send_message():
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        except Exception as e:
            print(f"[TelegramBot] Error sending message: {e}")

    # Запуск asyncio-корутины в потоке безопасно
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_message())
    except RuntimeError:
        # We're in a different thread — no loop running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_message())
        loop.close()
