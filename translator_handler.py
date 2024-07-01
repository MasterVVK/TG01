import logging
from aiogram import Router, F
from aiogram.types import Message
from googletrans import Translator

# Создание экземпляра маршрутизатора
router = Router()

translator = Translator()

@router.message(F.text)
async def handle_text(message: Message):
    logging.info("Получено текстовое сообщение для перевода")

    # Проверяем, что текст не является командой
    if message.text.startswith('/'):
        return

    try:
        translation = translator.translate(message.text, dest='en')
        await message.reply(translation.text)
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.reply("Ошибка перевода. Попробуйте позже.")
