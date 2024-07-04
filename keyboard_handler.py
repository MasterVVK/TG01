import logging
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создание маршрутизатора
router = Router()

# Создание клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Привет"),
            KeyboardButton(text="Пока")
        ]
    ],
    resize_keyboard=True
)

# Обработчик кнопки "Привет"
@router.message(F.text == "Привет")
async def handle_hello(message: types.Message):
    logging.info("Нажата кнопка Привет")
    await message.reply(f"Привет, {message.from_user.first_name}!")

# Обработчик кнопки "Пока"
@router.message(F.text == "Пока")
async def handle_goodbye(message: types.Message):
    logging.info("Нажата кнопка Пока")
    await message.reply(f"До свидания, {message.from_user.first_name}!")
