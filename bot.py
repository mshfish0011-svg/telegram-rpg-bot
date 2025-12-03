import logging
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os

# Load the .env file to get the bot token
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin panel access (replace with your admin's Telegram ID)
ADMIN_ID = 'your_admin_telegram_id_here'

# User data storage (to simulate progress and levels)
user_data = {}

# States for the conversation handler
START, CHARACTER_NAME, CHARACTER_GENDER, CHARACTER_CLASS, CHARACTER_STATS, MAIN_MENU = range(6)

# Check if the user is admin
def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == ADMIN_ID

# Command to access the admin panel
def admin_panel(update: Update, context: CallbackContext) -> None:
    if is_admin(update):
        update.message.reply_text("Welcome to the Admin Panel!\nHere you can check user stats, top players, etc.")
        show_user_stats(update)
    else:
        update.message.reply_text("You do not have access to the Admin Panel.")

# Show user stats
def show_user_stats(update: Update) -> None:
    active_users = len([user for user in user_data.values() if user.get('active', False)])
    total_users = len(user_data)
    top_players = sorted(user_data, key=lambda x: user_data[x].get('level', 0), reverse=True)[:5]

    stats_message = (
        f"Total Users: {total_users}\n"
        f"Active Users: {active_users}\n"
        f"Top 5 Players:\n" +
        "\n".join(f"{i+1}. {user_data[player]['name']} (Level: {user_data[player]['level']})" for i, player in enumerate(top_players))
    )

    update.message.reply_text(stats_message)

# Start the conversation and show the welcome screen
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_data[user_id] = {'stats': {'strength': 0, 'agility': 0, 'intelligence': 0}, 'level': 1}

    update.message.reply_text(
        "Welcome to the World of [Game Name]!\n\n"
        "Ready to begin your adventure?\n\n"
        "Type /start to create your character.",
        reply_markup=None
    )
    return CHARACTER_NAME

# Character name input
def character_name(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("What is your character's name?")
    return CHARACTER_GENDER

# Choose gender
def character_gender(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    name = update.message.text
    user_data[user_id]['name'] = name
    update.message.reply_text("Choose your character's gender:\n1. Male\n2. Female")
    return CHARACTER_CLASS

# Choose class
def character_class(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    gender = update.message.text
    user_data[user_id]['gender'] = gender
    update.message.reply_text("Choose your class:\n1. Wizard\n2. Warrior\n3. Archer")
    return CHARACTER_STATS

# Set stats (Strength, Agility, Intelligence)
def character_stats(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    char_class = update.message.text
    user_data[user_id]['class'] = char_class

    update.message.reply_text(
        f"Class: {char_class} - Now, distribute your initial stats:\n"
        "Strength (0-10):\n"
        "Agility (0-10):\n"
        "Intelligence (0-10):"
    )
    return MAIN_MENU

# Show the main menu with actions
def main_menu(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    stats = user_data[user_id]['stats']
    update.message.reply_text(
        f"Character Profile:\n"
        f"Name: {user_data[user_id]['name']}\n"
        f"Gender: {user_data[user_id]['gender']}\n"
        f"Class: {user_data[user_id]['class']}\n"
        f"Stats: Strength: {stats['strength']} Agility: {stats['agility']} Intelligence: {stats['intelligence']}\n\n"
        "You can now start exploring the world!\n\n"
        "/explore - Begin your journey!\n"
        "/inventory - View your inventory",
        reply_markup=None
    )
    return ConversationHandler.END

# /explore command to simulate map exploration
def explore(update: Update, context: CallbackContext) -> None:
    locations = ["Forest of Shadows", "Dungeon of Doom", "Merchant District", "Mysterious Cave"]
    random_location = random.choice(locations)
    update.message.reply_text(f"You're exploring the {random_location}!\nWhat will you do next?")

# Main function to set up the bot and handlers
def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHARACTER_NAME: [MessageHandler(Filters.text & ~Filters.command, character_name)],
            CHARACTER_GENDER: [MessageHandler(Filters.text & ~Filters.command, character_gender)],
            CHARACTER_CLASS: [MessageHandler(Filters.text & ~Filters.command, character_class)],
            CHARACTER_STATS: [MessageHandler(Filters.text & ~Filters.command, character_stats)],
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, main_menu)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("explore", explore))
    dp.add_handler(CommandHandler("admin", admin_panel))  # Admin panel command

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
