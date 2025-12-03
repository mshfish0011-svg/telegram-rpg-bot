import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging

# فعال کردن لاگ‌ها
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات که از BotFather دریافت کردی
TOKEN = '8208865404:AAFVWngVgXT5fQYAJNxLej9yuEdvafx5OrE'

# ID مدیر ربات (شما باید ID خودتون رو اینجا وارد کنید)
ADMIN_ID = 7681488759  # جای این عدد رو با ID خودتون عوض کنید

# تابعی که برای دستور /start اجرا میشه
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {update.message.from_user.username} with ID {user_id} started the bot.")
    if user_id == ADMIN_ID:
        await update.message.reply_text('سلام مدیر عزیز! از طریق دکمه‌ها تغییرات رو انجام بده.')
    else:
        await update.message.reply_text('سلام! خوش اومدی به ربات RPG.')

# دستور مدیر برای دسترسی به پنل
async def admin_panel(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {update.message.from_user.username} requested admin panel.")
    if user_id == ADMIN_ID:
        await update.message.reply_text('این پنل مدیریتی است. از اینجا می‌تونی تغییرات رو انجام بدی.')
    else:
        await update.message.reply_text('شما دسترسی به این بخش ندارید.')

# اجرای ربات
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # افزودن دستور start و پنل مدیریتی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin_panel", admin_panel))

    # پورت خود را از رندر دات کام بگیریم
    port = int(os.environ.get("PORT", 5000))  # پورت مشخص شده
    logger.info(f"Using port: {port}")  # لاگ برای بررسی
    application.run_polling(port=port)

if __name__ == '__main__':
    main()
