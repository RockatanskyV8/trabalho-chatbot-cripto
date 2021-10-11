from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from session_manager import SessionManager

import configparser
import assistente
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('TelegramBot')

config = configparser.ConfigParser()
config.read('config.ini')

TELEGRAM_BOT_TOKEN = config['TELEGRAM']['BOT_TOKEN']

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Olá, esse é um bot de teste')

def message(update, context):
    message_received = update.message.text

    assistente.validate_session(update.effective_chat.id)

    response_text = assistente.send_message(SessionManager.getInstance().getSession(update.effective_chat.id), update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.text, message)
dispatcher.add_handler(message_handler)

updater.start_polling()
