from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from session_manager import SessionManager

import assistente
import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('TelegramBot')

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK')

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def setup():
    #cria updater e dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    #define handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    message_handler = MessageHandler(Filters.text, message)
    dispatcher.add_handler(message_handler)

    #inicia webhook com a porta configurada pelo heroku
    #o heroku cuida automaticamente do proxy reverso, portanto a porta deve ser a fornecida pelo heroku
    #nas variáveis de ambiente
    updater.start_webhook(listen='0.0.0.0',
                          port=PORT,
                          url_path=TELEGRAM_BOT_TOKEN,
                          webhook_url='https://trabalho-chatbot-py.herokuapp.com/' + TELEGRAM_BOT_TOKEN)

    #configura webhook
    updater.bot.set_webhook(WEBHOOK_URL + '/' + TELEGRAM_BOT_TOKEN)

    #para a aplicacao nao terminar, eh necessario chamar o idle para que ela fique sempre rodando
    updater.idle()

    return (updater, dispatcher)

def start(update, context):
    assistente.validate_session(update.effective_chat.id)
    response_text = assistente.send_message(SessionManager.getInstance().getSession(update.effective_chat.id), '')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Olá, esse é um bot de teste')

def message(update, context):
    message_received = update.message.text

    assistente.validate_session(update.effective_chat.id)

    response_text = assistente.send_message(SessionManager.getInstance().getSession(update.effective_chat.id), update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

