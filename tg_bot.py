import re
import logging
import requests

from datetime import datetime

from telegram import Bot

from telegram import ForceReply, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters


chat_history: dict[str, dict[str, str]] = {}
TOKEN = "000000000000000000000000000000000000000000000"
bot = Bot(token=TOKEN)
url = "http://0.0.0.0:8000/question/"
headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Приветствую тебя, {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user = re.search(r'\d+', (update.effective_user.mention_html())).group()
    if current_user not in chat_history:
        chat_history[current_user] = {}
        chat_history[current_user]["session_start"] = current_time
        chat_history[current_user]["no_count"] = 0
    chat_history[current_user][current_time] = "Started chat"
    chat_history[current_user]["operator"] = False


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user = re.search(r'\d+', (update.effective_user.mention_html())).group()
    if current_user not in chat_history:
        chat_history[current_user] = {}
        chat_history[current_user]["session_start"] = current_time
        chat_history[current_user]["operator"] = False
        chat_history[current_user]["no_count"] = 0
    chat_history[current_user][current_time] = update.message.text


async def reply_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to the user message."""
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes"),
            InlineKeyboardButton("Нет", callback_data="no"),
        ],
        # [InlineKeyboardButton("Позвать оператора", callback_data="operator")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user = re.search(r'\d+', (update.effective_user.mention_html())).group()
    if current_user not in ["5102500090", "174239890"]:
        if current_user not in chat_history:
            chat_history[current_user] = {}
            chat_history[current_user]["session_start"] = current_time
            chat_history[current_user]["operator"] = False
            chat_history[current_user]["no_count"] = 0
        chat_history[current_user][current_time] = update.message.text
        if update.message.text == "debug":
            await update.message.reply_text(f"{chat_history}")

        if chat_history[current_user]["operator"] == False:
            data = {'question': f'{update.message.text}'}
            response = requests.post(url, headers=headers, json=data)
            await update.message.reply_text(f"Ответ:\r\n{response.json()['msg']}\r\n\r\nЭтот ответ удовлетворяет запросу?", reply_markup=reply_markup)

        if chat_history[current_user]["operator"] == True:
            reply = f"\r\nTEST OPERATOR REPLY"
            # await update.message.reply_text(f"Напишите вопрос оператору:")
            await bot.send_message(chat_id=174239890, text=f"id={current_user}: \r\n{update.message.text.replace('operator ', '')}") # "340009341"
            await bot.send_message(chat_id=5102500090, text=f"id={current_user}: \r\nhistory: {chat_history[current_user]}\r\n\r\nmessage:\r\n{update.message.text.replace('operator ', '')}") # "340009341"

    if update.message.text.lower().startswith("operator ") or current_user in ["5102500090"]:#, "174239890"]:
        # await update.message.reply_text(f"{update.message.text.replace('operator ', '')}")
        if any(char.isdigit() for char in update.message.text):
            user_to_answer = re.search(r'\d+', (update.message.text)).group()
            await bot.send_message(chat_id=user_to_answer, text=update.message.text.replace('operator ', '').replace(user_to_answer, '')) # "340009341"
        else:
            await update.message.reply_text(f"Укажи id пользователя")
                
    print(chat_history)
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes"),
            InlineKeyboardButton("Нет", callback_data="no"),
        ],
        # [InlineKeyboardButton("Позвать оператора", callback_data="operator")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user = re.search(r'\d+', (update.effective_user.mention_html())).group()
    if current_user not in chat_history:
        chat_history[current_user] = {}
    chat_history[current_user][current_time] = f"Choise: {query.data}"
    if query.data == "operator":
        chat_history[current_user]["operator"] = True
        await query.edit_message_text(text=f"Напишите вопрос оператору:")
    elif query.data == "yes":
        # await query.edit_message_text(text=f"Selected option: {query.data}")
        await query.edit_message_text(text=f"Спасибо за обращение.\r\nДо свидания!")
    elif query.data == "no":
        # await query.edit_message_text(text=f"Selected option: {query.data}")
        chat_history[current_user]["no_count"] += 1
        
        await query.edit_message_text(text=f"Уточняющий вопрос #{chat_history[current_user]['no_count']}")
        if chat_history[current_user]["no_count"] >= 5:
            chat_history[current_user]["operator"] = True
            await query.edit_message_text(text=f"Напишите вопрос оператору:")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_user))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
