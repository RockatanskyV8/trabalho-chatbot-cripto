from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import configparser
from session_manager import SessionManager
from pycoingecko import CoinGeckoAPI

import logging

logger = logging.getLogger('TelegramBot')

config = configparser.ConfigParser()
config.read('config.ini')

authenticator = IAMAuthenticator(config['WATSON_ASSISTANT']['IAM_TOKEN'])

assistant_id = config['WATSON_ASSISTANT']['ASSISTANT_ID']

URL = config['WATSON_ASSISTANT']['URL']

cg = CoinGeckoAPI()

assistant = AssistantV2(
    version='2020-02-05',
    authenticator=authenticator
)

assistant.set_service_url(URL)

def create_session():
    response = assistant.create_session(assistant_id)
    return response.get_result()['session_id']

def validate_session(chat_id):
    # check if session is valid for current chat_id
    logger.info('Validando sessão de ' + str(chat_id))
    if not SessionManager.getInstance().checkSession(chat_id):
        session_id = create_session()
        logger.info('Sessão criada para ' + str(chat_id))
    else:
        session_id = SessionManager.getInstance().getSession(chat_id)
        logger.info('Sessão atualizada para ' + str(chat_id))

    SessionManager.getInstance().updateSession(chat_id, session_id)

def send_message(session_id, message):
    logger.info('Enviando mensagem para o Assistant: ' + message)
    response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input = {
            'message_type': 'text',
            'text': message
        }
    )
    result = response.get_result()

    reply = ""
    
    if( len(result['output']['entities']) > 0 and result['output']['entities'][0]['entity'] == 'crypto'):
        crypto = (result['output']['entities'][0]['value']).lower()
        value  = cg.get_price(ids=crypto, vs_currencies='brl,usd,eur')
        reply  = reply + crypto + "\n" + "BRL " + str(value[crypto]['brl'] ) + "\n" + "USD " + str(value[crypto]['eur'] ) + "\n" + "EUR " + str(value[crypto]['usd'] ) + "\n"

    if( len( result['output']['generic'] ) > 0 ):
        reply = reply + result['output']['generic'][0]['text']
    
    logger.info('Recebido do assistant: ' + reply)

    return reply
