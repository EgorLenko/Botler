import asyncio
import os

import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command, Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from modules.Weather import WeatherData

logging.basicConfig(level=logging.INFO)

load_dotenv(".env")

BOTLER_TOKEN = os.environ.get('BOTLER_API_TOKEN')

botler = Bot(token=BOTLER_TOKEN)
disp = Dispatcher(botler)
disp.middleware.setup(LoggingMiddleware())


@disp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    welcome_text = (
        "Welcome to the bot! Here are the available commands:\n"
        "/start - Show this welcome message and available commands\n"
        "/help - Show all available commands"
        "/weather - Request your location for weather information\n"
    )
    print(f'{type(message)}, {message=}')
    await message.reply(welcome_text)


@disp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(
        "Hi! I'm glad to help you!\nMy name - 'Botler' - your daily helper.\nFor  now i can help you:\n• Get whether "
        "for your location;\n")
    await message.reply(
        "Function that don't implement yet:\n• News Digest;\n• To-Do List;\n• Productivity;\n• Local Events\n and more!")


async def send_location_reminder(chat_id, timeout=15):
    await asyncio.sleep(timeout)
    if chat_id not in user_location_received:
        await botler.send_message(chat_id, "Sorry, we didn't receive your location. Please check your geolocation and "
                                           "press the 'Send my location' button.")


@disp.message_handler(Command('weather'))
async def weather(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Send my location", request_location=True))
    sent_message = await message.reply("Please, press the button below to share your location:", reply_markup=keyboard)
    chat_id = sent_message.chat.id
    asyncio.create_task(send_location_reminder(chat_id))


@disp.callback_query_handler(Text(equals='request_location'))
async def handle_request_location_callback(query: types.CallbackQuery):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Send my location", request_location=True))

    sent_message = await query.message.reply("Please, press the button below to share your location:",
                                             reply_markup=keyboard)
    await query.answer()

    chat_id = sent_message.chat.id
    asyncio.create_task(send_location_reminder(chat_id))


user_location_received = set()


@disp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    user_latitude, user_longitude = message.location.latitude, message.location.longitude
    user_location_received.add(message.chat.id)
    weather = WeatherData(latitude=user_latitude, longitude=user_longitude)
    weather_msg = f'Your weather for today:\n {weather.data}'
    await message.reply(weather_msg)


if __name__ == '__main__':
    executor.start_polling(disp, skip_updates=True)
