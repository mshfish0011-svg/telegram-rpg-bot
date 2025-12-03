import logging
import random
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# Load .env for local dev; in Render you should set ENV vars in the dashboard
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID_ENV = os.getenv("ADMIN_ID")  # optional

# Basic checks
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set. Set it in environment variables.")

try:
    ADMIN_ID = int(ADMIN_ID_ENV) if ADMIN_ID_ENV else None
except ValueError:
    ADMIN_ID = None

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory user store (use a real DB in production)
user_data = {}

# Conversation states
START, CHARACTER_NAME, CHARACTER_GENDER, CHARACTER_CLASS, CHARACTER_STATS = range(5)

def is_admin(update: Update) -> bool:
    user = update.effective_user
    return (ADMIN_ID is not None) and (user is not None) and (user.id == ADMIN_ID)

async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_users = len(user_data)
    active_users = len([u for u in user_data.values() if u.get("active")])
    # sort by level (if present)
    top_players = sorted(user_data.items(), key=lambda kv: kv[1].get("level", 0), reverse=True)[:5]

    lines = [f"Total Users: {total_users}", f"Active Users: {active_users}", "Top 5 Players:"]
    for i, (uid, data) in enumerate(top_players):
        name = data.get("name", f"User {uid}")
        level = data.get("level", 1)
        lines.append(f"{i+1}. {name} (Level: {level})")

    await update.message.reply_text("\n".join(lines))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_admin(update):
        await update.message.reply_text("Welcome to the Admin Panel!\nHere you can check user stats, top players, etc.")
        await show_user_stats(update, context)
    else:
        await update.message.reply_text("You do not have access to the Admin Panel.")

# Start -> ask for name
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if user is None:
        return ConversationHandler.END
    user_id = user.id
    # initialize minimal user state
    user_data.setdefault(user_id, {"stats": {"strength": 0, "agility": 0, "intelligence": 0}, "level": 1, "active": True})
    await update.message.reply_text(
        "Welcome to the World of [Game Name]!\nLet's create your character.\n\nWhat is your character's name?"
    )
    return CHARACTER_NAME

# CHARACTER_NAME -> store name, ask gender
async def character_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if user is None:
        return ConversationHandler.END
    user_id = user.id
    name = update.message.text.strip()
    user_data[user_id]["name"] = name
    await update.message.reply_text("Choose your character's gender:\n1. Male\n2. Female\n(Reply with 1 or 2 or type Male/Female)")
    return CHARACTER_GENDER

# CHARACTER_GENDER -> store gender, ask class
async def character_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip().lower()
    if text in ("1", "male", "m"):
        gender = "Male"
    elif text in ("2", "female", "f"):
        gender = "Female"
    else:
        await update.message.reply_text("Invalid choice. Reply with 1 for Male or 2 for Female.")
        return CHARACTER_GENDER

    user_data[user_id]["gender"] = gender
    await update.message.reply_text("Choose your class:\n1. Wizard\n2. Warrior\n3. Archer\n(Reply with 1/2/3 or the class name)")
    return CHARACTER_CLASS

# CHARACTER_CLASS -> store class, ask for stats distribution
async def character_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip().lower()
    classes = {"1": "Wizard", "2": "Warrior", "3": "Archer", "wizard": "Wizard", "warrior": "Warrior", "archer": "Archer"}
    chosen = classes.get(text)
    if not chosen:
        await update.message.reply_text("Invalid class. Reply with 1/2/3 or Wizard/Warrior/Archer.")
        return CHARACTER_CLASS

    user_data[user_id]["class"] = chosen
    await update.message.reply_text(
        "Distribute 10 points among Strength, Agility, Intelligence.\n"
        "Reply with three numbers separated by spaces, e.g.:\n3 4 3"
    )
    return CHARACTER_STATS

# CHARACTER_STATS -> parse, validate, finish
async def character_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()
    parts = text.split()
    if len(parts) != 3:
        await update.message.reply_text("Please reply with exactly three numbers, e.g. `3 4 3`.")
        return CHARACTER_STATS
    try:
        s, a, i = map(int, parts)
    except ValueError:
        await update.message.reply_text("All values must be integers.")
        return CHARACTER_STATS

    total = s + a + i
    if total != 10:
        await update.message.reply_text("Total must equal 10. Try again.")
        return CHARACTER_STATS
    for val in (s, a, i):
        if val < 0 or val > 10:
            await update.message.reply_text("Each value must be between 0 and 10.")
            return CHARACTER_STATS

    user_data[user_id]["stats"] = {"strength": s, "agility": a, "intelligence": i}
    await update.message.reply_text(
        f"Character created!\nName: {user_data[user_id]['name']}\n"
        f"Gender: {user_data[user_id]['gender']}\n"
        f"Class: {user_data[user_id]['class']}\n"
        f"Stats: Strength {s}, Agility {a}, Intelligence {i}\n\n"
        "You can now start exploring: /explore\nCheck inventory: /inventory"
    )
    return ConversationHandler.END

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    locations = ["Forest of Shadows", "Dungeon of Doom", "Merchant District", "Mysterious Cave"]
    location = random.choice(locations)
    await update.message.reply_text(f"You're exploring the {location}!\nWhat will you do next?")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    data = user_data.get(user.id, {})
    inv = data.get("inventory", [])
    if not inv:
        await update.message.reply_text("Your inventory is empty.")
    else:
        await update.message.reply_text("Your inventory:\n" + "\n".join(inv))

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHARACTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_name)],
            CHARACTER_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_gender)],
            CHARACTER_CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_class)],
            CHARACTER_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_stats)],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("explore", explore))
    application.add_handler(CommandHandler("inventory", inventory))
    application.add_handler(CommandHandler("admin", admin_panel))

    # For Render: if you plan to use polling, add this as a Background Worker with command "python bot.py"
    # For webhooks: implement a webhook endpoint and use application.run_webhook(...)
    application.run_polling()

if __name__ == "__main__":
    main()
