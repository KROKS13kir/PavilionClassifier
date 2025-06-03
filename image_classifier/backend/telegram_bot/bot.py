# telegram_bot/bot.py

import pytz
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes, CallbackQueryHandler,
)
from asgiref.sync import sync_to_async
from django.conf import settings

from classifier.models import Employee, RepairOrder

from classifier.utils import generate_presigned_url

# Обёртки для синхронных ORM-вызовов
get_employee_by_token = sync_to_async(Employee.objects.get, thread_sensitive=True)
get_employee_by_chat = sync_to_async(Employee.objects.get, thread_sensitive=True)
save_employee = sync_to_async(Employee.save, thread_sensitive=True)
fetch_orders = sync_to_async(list, thread_sensitive=True)  # превращает QuerySet в list

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start <telegram_token> — привязываем chat_id к сотруднику
    """
    if not context.args:
        await update.message.reply_text("Пожалуйста, пришлите команду /start <ваш токен>")
        return

    token = context.args[0]
    try:
        emp = await get_employee_by_token(telegram_token=token)
        emp.telegram_chat_id = update.effective_chat.id
        await save_employee(emp)
        await update.message.reply_text(f"Привет, {emp.full_name}! Ваш чат привязан.")
    except Employee.DoesNotExist:
        await update.message.reply_text("Токен некорректен, обратитесь к администратору.")

async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /orders — показать все наряды, назначенные текущему сотруднику
    """
    chat_id = update.effective_chat.id

    def _fetch_and_format(chat_id):
        # 1) находим сотрудника по chat_id
        emp = Employee.objects.get(telegram_chat_id=chat_id)
        # 2) забираем все его наряды с привязкой Pavilion (select_related)
        qs = (
            RepairOrder.objects
            .filter(employee=emp)
            .select_related('pavilion')
            .order_by('-scheduled_for')
        )
        if not qs:
            return []
        # 3) форматируем каждую строку
        return [
            f"#{o.id} {o.pavilion.stop_name} "
            f"({o.scheduled_for:%d.%m.%Y}) — {o.get_status_display()}"
            for o in qs
        ]

    try:
        lines = await sync_to_async(_fetch_and_format, thread_sensitive=True)(chat_id)
    except Employee.DoesNotExist:
        await update.message.reply_text(
            "❗ Сначала привяжите аккаунт:\n"
            "`/start <ваш токен>`",
            parse_mode="Markdown"
        )
        return

    if not lines:
        await update.message.reply_text("У вас пока нет нарядов.")
    else:
        await update.message.reply_text("\n".join(lines))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 Доступные команды:\n"
        "/start <токен> — привязать Telegram к профилю\n"
        "/orders — список назначенных нарядов\n"
        "/order <id> — детали наряда\n"
        "/set_status <id> — изменить статус наряда кнопкой\n"
        "/help — показать эту справку"
    )
    await update.message.reply_text(text)


from telegram import InputMediaPhoto

async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите номер наряда, например: /order 5")
        return

    try:
        order_id = int(context.args[0])
        chat_id = update.effective_chat.id

        def _get_order_detail(order_id, chat_id):
            emp = Employee.objects.get(telegram_chat_id=chat_id)
            order = (
                RepairOrder.objects
                .select_related('pavilion')
                .prefetch_related('images__image')
                .get(id=order_id, employee=emp)
            )

            pavilion = order.pavilion
            images = [generate_presigned_url(rel.image.image_url) for rel in order.images.all()]

            damage_states = ['граффити', 'плановый ремонт', 'срочный ремонт']
            last_damaged = (
                pavilion.images
                .filter(confirmed_state__in=damage_states)
                .order_by('-uploaded_at')
                .first()
            )

            message = (
                f"🔧 Наряд #{order.id}\n"
                f"📍 Остановка: {pavilion.stop_name} ({pavilion.mpv_code})\n"
                f"🏷 Номер павильона: {pavilion.pavilion_number}\n"
                f"📫 Адрес: {pavilion.address or '—'}\n"
                f"⚠️ Проблема: {last_damaged.confirmed_state if last_damaged else '—'}\n"
                f"📝 Описание: {order.description or '—'}\n"
                f"📌 Статус: {order.get_status_display()}\n"
                f"🔥 Приоритет: {order.get_priority_display()}"
            )

            return message, images

        message, image_urls = await sync_to_async(_get_order_detail, thread_sensitive=True)(order_id, chat_id)

        await update.message.reply_text(message)

        if image_urls:
            media = [InputMediaPhoto(media=url) for url in image_urls[:10]]
            await context.bot.send_media_group(chat_id=chat_id, media=media)

    except (ValueError, RepairOrder.DoesNotExist, Employee.DoesNotExist):
        await update.message.reply_text("❗ Наряд не найден или вам не назначен.")



STATUS_CHOICES = {
    k: v for k, v in dict(RepairOrder.STATUS_CHOICES).items()
    if k != 'new'
}


async def set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите ID наряда: /set_status <id>")
        return

    order_id = context.args[0]
    chat_id = update.effective_chat.id

    # Проверим, есть ли такой наряд
    try:
        def _check_order(order_id, chat_id):
            emp = Employee.objects.get(telegram_chat_id=chat_id)
            return RepairOrder.objects.get(id=order_id, employee=emp)

        await sync_to_async(_check_order, thread_sensitive=True)(order_id, chat_id)
    except (RepairOrder.DoesNotExist, Employee.DoesNotExist):
        await update.message.reply_text("❗ Наряд не найден или вам не назначен.")
        return

    # Генерируем кнопки
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"status:{order_id}:{value}")]
        for value, label in STATUS_CHOICES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Выберите новый статус для наряда #{order_id}:",
        reply_markup=reply_markup
    )


async def handle_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, order_id, new_status = query.data.split(":")
        chat_id = query.from_user.id

        def _update_status(order_id, new_status, chat_id):
            emp = Employee.objects.get(telegram_chat_id=chat_id)
            order = RepairOrder.objects.get(id=order_id, employee=emp)
            order.status = new_status
            order.save()
            return order

        order = await sync_to_async(
            _update_status,
            thread_sensitive=True
        )(order_id, new_status, chat_id)

        await query.edit_message_text(
            f"✅ Статус наряда #{order.id} обновлён на {order.get_status_display()}"
        )
    except Exception as e:
        await query.edit_message_text("⚠️ Ошибка при обновлении статуса.")
        print(f"Ошибка в handle_status_callback: {e}")





def build_app():
    # Функция, которая установит список команд у бота
    async def set_bot_commands(application):
        await application.bot.set_my_commands([
            BotCommand("start", "Привязать аккаунт к боту"),
            BotCommand("orders", "Показать ваши наряды"),
            BotCommand("help", "Справка по командам"),
            BotCommand("order", "Показать детали наряда по ID"),
            BotCommand("set_status", "Изменить статус наряда"),
        ])

    # Собираем приложение
    app = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_TOKEN)
        .post_init(set_bot_commands)
        .build()
    )

    # Регистрируем хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("order", order_details))
    app.add_handler(CommandHandler("set_status", set_status))
    app.add_handler(CallbackQueryHandler(handle_status_callback, pattern=r"^status:\d+:.+"))

    return app


