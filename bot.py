from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging

# فعال کردن لاگ‌ها
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات که از BotFather دریافت کردی
TOKEN = '8208865404:AAFVWngVgXT5fQYAJNxLej9yuEdvafx5OrE'

# تابعی که برای دستور /start اجرا میشه
async def start(update: Update, context: CallbackContext) -> None:
    logger.info(f'User {update.message.from_user.username} started the bot')
    await update.message.reply_text('سلام! به ربات RPG خوش اومدی.')

# اصلی‌ترین قسمت برنامه
def main() -> None:
    # اتصال به ربات با استفاده از توکن
    application = Application.builder().token(TOKEN).build()

    # افزودن دستور start
    application.add_handler(CommandHandler("start", start))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
