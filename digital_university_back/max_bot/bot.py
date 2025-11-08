from maxapi import Bot
import asyncio
import structlog
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, Message, MessageCreated, Command
from dotenv import load_dotenv
import os
load_dotenv()
LOG = structlog.getLogger()

bot = Bot(os.getenv("MAX_TOKEN")) # инстанс бота
dp = Dispatcher() # диспетчер
@dp.bot_started() # действие при запуске
async def start_bot(event: BotStarted): # в ивенты передаем тип события
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="plaintext"
    )
# базовый ответ на сообщение 
dp.message_created(Command('start')) # при получении /команда
async def greet(event: MessageCreated):
    await event.message.answer("plaintext")
# запуск бота
async def main():
    await dp.start_polling(bot)


asyncio.run(main())