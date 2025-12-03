import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN", "")

STORY_FILE = "story.json"
SAVES_DIR = "saves"

if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

# Load story
with open(STORY_FILE, "r", encoding="utf-8") as f:
    STORY = json.load(f)

def save_path(user_id):
    return os.path.join(SAVES_DIR, f"{user_id}.json")

def load_player(user_id):
    path = save_path(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"node": "start"}

def save_player(user_id, state):
    with open(save_path(user_id), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def render_node(state):
    node_id = state["node"]
    node = STORY.get(node_id)
    if not node:
        return ("پایان بازی یا خطا.", [])

    text = node.get("text", "")
    buttons = []
    for i, choice in enumerate(node.get("choices", [])):
        buttons.append([InlineKeyboardButton(choice["text"], callback_data=str(i))])

    return text, buttons

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    state = load_player(user.id)

    text, buttons = render_node(state)
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text, reply_markup=keyboard)

def callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    query.answer()

    state = load_player(user.id)
    node = STORY.get(state["node"])
    idx = int(query.data)
    choices = node.get("choices", [])
    if idx < 0 or idx >= len(choices):
        query.edit_message_text("Invalid choice.")
        return

    next_node = choices[idx]["next"]
    state["node"] = next_node
    save_player(user.id, state)

    text, buttons = render_node(state)
    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text, reply_markup=keyboard)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callback_query))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
