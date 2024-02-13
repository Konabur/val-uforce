import aiogram
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import os
import random
import logging
import asyncio

if '.env' in os.listdir():
    from dotenv import load_dotenv
    load_dotenv()

# = НАСТРОЙКИ = #
# user_id админа, загружающего фотки в бота
ADMIN_TG_ID = 308133526
# Папка для загруженных файлов
DESTINATION_DIR = 'sources'
# Изначальное количество картинок 
# (нужно поставить конкретное число, чтобы 
# не сбивался порядок, если будет загрузка 
# во время работы бота)
FIRST_COUNT = DESTINATION_DIR + '/'


dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user = message.from_user.username or message.from_user.id
    logging.info(f'@{user} /start')
    k = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='Покажи ещё!', callback_data='0')
    ]])
    await message.answer(
        "Привет, работяга! Надеюсь, ты готов получить лучшую валентинку за всю свою карьеру 💜",
        reply_markup=k
    )

@dp.message(F.photo)
async def add_photo(message: types.Message):
    if message.from_user.id != ADMIN_TG_ID:
        return await asyncio.sleep(0)
    user = message.from_user.username or message.from_user.id
    path = f'{DESTINATION_DIR}/documents/{message.document.file_name}'
    await message.bot.download(message.photo, destination=path)
    logging.info(f'@{user} uploaded photo to {path}')
    await message.reply(f'Добавил в папку {DESTINATION_DIR}')

@dp.message(F.document)
async def add_file(message: types.Message):
    if message.from_user.id != ADMIN_TG_ID:
        return await asyncio.sleep(0)
    user = message.from_user.username or message.from_user.id
    path = f'{DESTINATION_DIR}/documents/{message.document.file_name}'
    await message.bot.download(message.document, destination=path)
    logging.info(f'@{user} uploaded photo (document) to {path}')
    await message.reply(f'Добавил в папку {DESTINATION_DIR}')

@dp.callback_query()
async def send_random_value(call: types.CallbackQuery):
    message = call.message
    try:
        await message.delete_reply_markup()
    except aiogram.exceptions.TelegramBadRequest:
        await call.answer()
        return
    index = int(call.data)
    user = str(message.chat.username or message.from_user.id)
    folder = f'{DESTINATION_DIR}/documents/'
    photos = os.listdir(folder)
    random.seed(message.from_user.id)
    random.shuffle(photos)
    photo = folder + photos[index]
    logging.info(f'used {photo=} for @{user}')
    k = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='Покажи ещё!', callback_data=str(index+1))
    ]])
    await message.answer_photo(types.FSInputFile(photo), caption='с 💜 от uForce', reply_markup=k)
    await call.answer()


async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt='%m-%d %H:%M:%S')
    logging.info('Bot is started')

    asyncio.run(main())
