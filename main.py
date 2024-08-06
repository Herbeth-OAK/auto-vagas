import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import CommandHandler, Application, CallbackContext
from telethon import TelegramClient
from datetime import datetime, timedelta, timezone

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
CHAT_ID = int(os.getenv('CHAT_ID')) 

bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

client = TelegramClient('session_name', API_ID, API_HASH)

async def get_messages_from_channel():
    await client.start(PHONE_NUMBER)
    date_limit = datetime.now(timezone.utc) - timedelta(days=1)
    messages = []

    entity = await client.get_entity('@CafeinaVagas')
    async for message in client.iter_messages(entity):
        if message.date >= date_limit:
            messages.append(f'{message.text}')
        else:
            break

    return messages

async def start(update: Update, context: CallbackContext):
    messages = await get_messages_from_channel()
    if messages:
        for msg in messages:
            await context.bot.send_message(chat_id=CHAT_ID, text=msg)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Nenhuma mensagem nas últimas 24 horas.")

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

if __name__ == '__main__':
    application.run_polling()
