import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from app import db, create_app
from app.models import Event, TelegramUser
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TITLE, DESCRIPTION, START_TIME, END_TIME = range(4)

class TelegramBot:
    def __init__(self):
        self.app = create_app()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        with self.app.app_context():
            telegram_user = TelegramUser.query.filter_by(telegram_id=str(user.id)).first()
            if not telegram_user:
                telegram_user = TelegramUser(
                    telegram_id=str(user.id),
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                db.session.add(telegram_user)
                db.session.commit()

        welcome_message = f"""
Привет, {user.first_name}! 👋

Я бот-календарь. Я помогу вам управлять событиями.

Доступные команды:
/start - Начать работу с ботом
/addevent - Добавить новое событие
/myevents - Показать мои события
/today - События на сегодня
/tomorrow - События на завтра
/week - События на неделю
/help - Помощь
        """
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
📅 Команды бота:

/addevent - Создать новое событие
/myevents - Посмотреть все события
/today - События на сегодня
/tomorrow - События на завтра
/week - События на ближайшую неделю
/help - Показать эту справку

Для создания события используйте /addevent и следуйте инструкциям.
        """
        await update.message.reply_text(help_text)

    async def add_event_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Давайте создадим новое событие! 📝\n\n"
            "Введите название события:"
        )
        return TITLE

    async def event_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['event_title'] = update.message.text
        await update.message.reply_text(
            "Отлично! Теперь введите описание события (или напишите 'пропустить'):"
        )
        return DESCRIPTION

    async def event_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        description = update.message.text
        context.user_data['event_description'] = '' if description.lower() == 'пропустить' else description

        await update.message.reply_text(
            "Введите дату и время начала события в формате:\n"
            "ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 25.12.2024 15:30"
        )
        return START_TIME

    async def event_start_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            start_time = datetime.strptime(update.message.text, '%d.%m.%Y %H:%M')
            context.user_data['event_start_time'] = start_time

            await update.message.reply_text(
                "Введите дату и время окончания события в формате:\n"
                "ДД.ММ.ГГГГ ЧЧ:ММ\n"
                "Например: 25.12.2024 16:30"
            )
            return END_TIME
        except ValueError:
            await update.message.reply_text(
                "Неправильный формат! Пожалуйста, используйте формат: ДД.ММ.ГГГГ ЧЧ:ММ\n"
                "Например: 25.12.2024 15:30"
            )
            return START_TIME

    async def event_end_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            end_time = datetime.strptime(update.message.text, '%d.%m.%Y %H:%M')

            if end_time <= context.user_data['event_start_time']:
                await update.message.reply_text(
                    "Время окончания должно быть позже времени начала!\n"
                    "Введите дату и время окончания снова:"
                )
                return END_TIME

            with self.app.app_context():
                event = Event(
                    title=context.user_data['event_title'],
                    description=context.user_data['event_description'],
                    start_time=context.user_data['event_start_time'],
                    end_time=end_time,
                    telegram_user_id=str(update.effective_user.id)
                )
                db.session.add(event)
                db.session.commit()

                await update.message.reply_text(
                    f"✅ Событие успешно создано!\n\n"
                    f"📌 {event.title}\n"
                    f"📝 {event.description}\n"
                    f"🕐 Начало: {event.start_time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"🕐 Конец: {event.end_time.strftime('%d.%m.%Y %H:%M')}"
                )

            context.user_data.clear()
            return ConversationHandler.END

        except ValueError:
            await update.message.reply_text(
                "Неправильный формат! Пожалуйста, используйте формат: ДД.ММ.ГГГГ ЧЧ:ММ\n"
                "Например: 25.12.2024 16:30"
            )
            return END_TIME

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Создание события отменено.",
            reply_markup=None
        )
        context.user_data.clear()
        return ConversationHandler.END

    async def my_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)

        with self.app.app_context():
            events = Event.query.filter_by(telegram_user_id=user_id).order_by(Event.start_time).all()

            if not events:
                await update.message.reply_text("У вас пока нет событий. Создайте событие с помощью /addevent")
                return

            message = "📅 Ваши события:\n\n"
            for event in events:
                message += f"📌 {event.title}\n"
                message += f"📝 {event.description}\n"
                message += f"🕐 {event.start_time.strftime('%d.%m.%Y %H:%M')} - {event.end_time.strftime('%H:%M')}\n\n"

            await update.message.reply_text(message)

    async def today_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        today = datetime.now().date()

        with self.app.app_context():
            events = Event.query.filter(
                Event.telegram_user_id == user_id,
                db.func.date(Event.start_time) == today
            ).order_by(Event.start_time).all()

            if not events:
                await update.message.reply_text("На сегодня событий нет! 🎉")
                return

            message = f"📅 События на сегодня ({today.strftime('%d.%m.%Y')}):\n\n"
            for event in events:
                message += f"📌 {event.title}\n"
                message += f"🕐 {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                if event.description:
                    message += f"📝 {event.description}\n"
                message += "\n"

            await update.message.reply_text(message)

    async def tomorrow_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        with self.app.app_context():
            events = Event.query.filter(
                Event.telegram_user_id == user_id,
                db.func.date(Event.start_time) == tomorrow
            ).order_by(Event.start_time).all()

            if not events:
                await update.message.reply_text("На завтра событий нет! 🎉")
                return

            message = f"📅 События на завтра ({tomorrow.strftime('%d.%m.%Y')}):\n\n"
            for event in events:
                message += f"📌 {event.title}\n"
                message += f"🕐 {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                if event.description:
                    message += f"📝 {event.description}\n"
                message += "\n"

            await update.message.reply_text(message)

    async def week_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        today = datetime.now()
        week_later = today + timedelta(days=7)

        with self.app.app_context():
            events = Event.query.filter(
                Event.telegram_user_id == user_id,
                Event.start_time >= today,
                Event.start_time <= week_later
            ).order_by(Event.start_time).all()

            if not events:
                await update.message.reply_text("На ближайшую неделю событий нет! 🎉")
                return

            message = "📅 События на ближайшую неделю:\n\n"
            for event in events:
                message += f"📌 {event.title}\n"
                message += f"📅 {event.start_time.strftime('%d.%m.%Y')}\n"
                message += f"🕐 {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                if event.description:
                    message += f"📝 {event.description}\n"
                message += "\n"

            await update.message.reply_text(message)

    def run(self):
        token = Config.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
            return

        application = Application.builder().token(token).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('addevent', self.add_event_start)],
            states={
                TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.event_title)],
                DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.event_description)],
                START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.event_start_time)],
                END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.event_end_time)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("myevents", self.my_events))
        application.add_handler(CommandHandler("today", self.today_events))
        application.add_handler(CommandHandler("tomorrow", self.tomorrow_events))
        application.add_handler(CommandHandler("week", self.week_events))

        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
