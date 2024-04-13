import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from cities import cities

TOKEN = ''

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())  


async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand("start", "Запустити бота"),
            types.BotCommand("show", "Показати усі доступні тури"),
            types.BotCommand(command="favorites", description="Показати обрані тури")
        ]
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    show_button = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Показати міста", callback_data="show cities")
    show_button.add(button)
    await message.answer(text="Вітаю! Я тур-бот, введи назву міста щоб дізнатись про найближчу екскурсію туди.\nАбо якщо не знаєш куди б ти хотів поїхати, то я можу показати список наших турів!", parse_mode="html", reply_markup=show_button)

@dp.message_handler(commands=["show"])
async def show(message: types.Message):
    cities_choice = InlineKeyboardMarkup()
    for city in cities:
        button = InlineKeyboardButton(text=city, callback_data=city)
        cities_choice.add(button)
    await message.answer(text="Оберіть місто:", parse_mode="html", reply_markup=cities_choice)

favorites_list = []

@dp.message_handler(commands=["favorites"])
async def favorites(message: types.Message):
    if favorites_list:
        show_favorites_list = InlineKeyboardMarkup()
        for favorit in favorites_list:
            favorit_button = InlineKeyboardButton(text=favorit, callback_data=f"favorite_{favorit}")
            show_favorites_list.add(favorit_button)
        await message.answer(text="Ось список обраного:", parse_mode="html" , reply_markup=show_favorites_list)
    else:
        await message.answer(text="Список обраного пустий!", parse_mode="html")


@dp.callback_query_handler(lambda callback_query: callback_query.data == "show cities")
async def show_cities(callback_query: types.CallbackQuery):
    cities_choice = InlineKeyboardMarkup()
    for city in cities:
        button = InlineKeyboardButton(text=city, callback_data=city)
        cities_choice.add(button)
    await bot.send_message(chat_id=callback_query.message.chat.id, text="Оберіть місто:", parse_mode="html", reply_markup=cities_choice)
    await callback_query.answer()

@dp.message_handler()
async def get_city(message: types.Message):
    city_name = message.text.capitalize()
    if "-" in city_name:
        city_parts = city_name.split("-")
        city_name = "-".join([part.capitalize() for part in city_parts])
    if city_name in cities:
        ph = cities[city_name]["photo"]
        url = cities[city_name]["site_url"]
        des = cities[city_name]["description"]
        p = cities[city_name]["price"]
        messag = f"<b>Інформація про екскурсію:</b>{des}\n\n<b>Посилання на сайт:</b>{url}\n\n<b>Ціна:</b>{p}"
        show_button = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="Додати в обране!", callback_data=f"cityn_{city_name}")
        show_button.add(button)
        await bot.send_photo(photo=ph, chat_id=message.chat.id)
        await message.answer(text=messag, parse_mode="html", reply_markup=show_button)
    else:
        await message.answer("Даний город відсутній у нашій базі.", parse_mode="html")

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("favorite_"))
async def use_favorite(callback_query: types.CallbackQuery):
    favorite_tour = callback_query.data.split("_")[1]
    if favorite_tour in cities:
        ph = cities[favorite_tour]["photo"]
        url = cities[favorite_tour]["site_url"]
        des = cities[favorite_tour]["description"]
        p = cities[favorite_tour]["price"]
        messag = f"<b>Інформація про екскурсію:</b>{des}\n\n<b>Посилання на сайт:</b>{url}\n\n<b>Ціна:</b>{p}"
        await bot.send_photo(photo=ph, chat_id=callback_query.message.chat.id)
        await bot.send_message(chat_id=callback_query.message.chat.id, text=messag, parse_mode="html")
        await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("cityn_")) 
async def favorite(callback_query: types.CallbackQuery):
    c_name = callback_query.data.split("_")[1]
    global favorites_list
    if c_name not in favorites_list:
        favorites_list.append(c_name)
        messag = f"Тур - {c_name}, додано до списку обраного!"
        await bot.send_message(chat_id=callback_query.message.chat.id, text=messag, parse_mode="html")
        await callback_query.answer()
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Цей тур є у списку обраного❗", parse_mode="html")
        await callback_query.answer()


@dp.callback_query_handler()
async def get_info(callback_query: types.CallbackQuery):
    city_name = callback_query.data
    if city_name in cities:
        ph = cities[city_name]["photo"]
        url = cities[city_name]["site_url"]
        des = cities[city_name]["description"]
        p = cities[city_name]["price"]
        messag = f"<b>Інформація про екскурсію:</b>{des}\n\n<b>Посилання на сайт:</b>{url}\n\n<b>Ціна:</b>{p}"
        show_button = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="Додати в обране!", parse_mode="html", callback_data=f"cityn_{city_name}")
        show_button.add(button)
        await bot.send_photo(photo=ph, chat_id=callback_query.message.chat.id)
        await bot.send_message(callback_query.message.chat.id, messag,  parse_mode="html", reply_markup=show_button)
        await callback_query.answer()
    else:
        await bot.send_message(callback_query.message.chat.id, text="Даний город відсутній у нашій базі.",  parse_mode="html")
        await callback_query.answer()
    

async def on_startup(dp):
    await set_default_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)