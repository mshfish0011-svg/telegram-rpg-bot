from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# توکن ربات که از BotFather دریافت کردی
TOKEN = '8208865404:AAFVWngVgXT5fQYAJNxLej9yuEdvafx5OrE'

# تابعی که برای دستور /start اجرا میشه
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('سلام! به ربات RPG خوش اومدی.')

# اصلی‌ترین قسمت برنامه
def main() -> None:
    # اتصال به ربات با استفاده از توکن
    updater = Updater(TOKEN)

    # گرفتن Dispatcher برای ارسال دستورات
    dispatcher = updater.dispatcher

    # افزودن دستور start
    dispatcher.add_handler(CommandHandler("start", start))

    # شروع ربات
    updater.start_polling()

    # منتظر دریافت پیام‌ها
    updater.idle()

if __name__ == '__main__':
    main()
