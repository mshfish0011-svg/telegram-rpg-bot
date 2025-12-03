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
    if user_id == ADMIN_ID:
        # اگر کاربر مدیر بود
        await update.message.reply_text('سلام مدیر عزیز! از طریق دکمه‌ها تغییرات رو انجام بده.')
    else:
        # اگر کاربر مدیر نبود
        await update.message.reply_text('سلام! خوش اومدی به ربات RPG.')

# دستور مدیر برای دسترسی به پنل
async def admin_panel(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        # پنل مدیریتی که فقط مدیر می‌تونه دسترسی داشته باشه
        await update.message.reply_text('این پنل مدیریتی است. از اینجا می‌تونی تغییرات رو انجام بدی.')
    else:
        await update.message.reply_text('شما دسترسی به این بخش ندارید.')

# اصلی‌ترین قسمت برنامه
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # افزودن دستور start و پنل مدیریتی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin_panel", admin_panel))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
