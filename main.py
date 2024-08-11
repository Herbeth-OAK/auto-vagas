import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import CommandHandler, Application, CallbackContext
from telethon import TelegramClient
from datetime import datetime, timedelta, timezone
import requests

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
CHAT_ID = int(os.getenv('CHAT_ID'))
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')
CHANNELS = os.getenv('CHANNELS').split(",")
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL')

KEYWORDS = ["desenvolvedor", "desenvolvedora", "desenvolvimento", "software", "híbrido", "remoto", "#hibrido", "#remoto", "oportunidade", "jr", "junior", "pleno", "back-end", "backend", "front-end", "frontend"]

bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()
client = TelegramClient('session_name', API_ID, API_HASH)

def message_contains_keywords(message_text):
    """Verifica se a mensagem contém alguma das palavras-chave."""
    if message_text is None:
        return False
    for keyword in KEYWORDS:
        if keyword.lower() in message_text.lower():
            return True
    return False

async def get_messages_from_channels():
    await client.start(PHONE_NUMBER)
    date_limit = datetime.now(timezone.utc) - timedelta(days=1)
    filtered_messages = []

    for channel in CHANNELS:
        entity = await client.get_entity(channel)
        async for message in client.iter_messages(entity):
            if message.date >= date_limit and message_contains_keywords(message.text):
                filtered_messages.append(f'{message.text}')
            elif message.date < date_limit:
                break

    return filtered_messages

async def start(update: Update, context: CallbackContext):
    messages = await get_messages_from_channels()
    if messages:
        for msg in messages:
            await context.bot.send_message(chat_id=CHAT_ID, text=msg)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Nenhuma mensagem relevante nas últimas 24 horas.")

def send_message_to_whatsapp(msg):
    """Envia uma mensagem para o WhatsApp usando a API."""
    payload = {
        'chatId': f'{WHATSAPP_NUMBER}@c.us',
        'contentType': 'string',
        'content': msg
    }
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json'
    }
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    print(response)
    return response

async def send(update: Update, context: CallbackContext):
    messages = await get_messages_from_channels()
    if messages:
        responses = list(map(send_message_to_whatsapp, messages))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Mensagens enviadas para o WhatsApp.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Nenhuma mensagem relevante nas últimas 24 horas.")

start_handler = CommandHandler('start', start)
send_handler = CommandHandler('send', send)

application.add_handler(start_handler)
application.add_handler(send_handler)

if __name__ == '__main__':
    application.run_polling()
