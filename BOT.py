import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from contextlib import suppress
from aiogram.utils.exceptions import MessageNotModified


logging.basicConfig(level=logging.INFO)
bot = Bot(token='6030262499:AAEx_4Vjej8GnXKVDmJzap2iPe1mjPrl0qQ')
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer('Привет.\nЯ бот, который может угадать любое число.\n'
                         'Набери "/numbers_fab" и загадай число.\n'
                         'Дальше просто отвечай:\n">", если твоё число больше, чем моё;\n"<", если оно меньше;\n"=", когда я угадаю.')


user_data = {}


async def update_num_text(message: types.Message, new_value: int):
    await message.edit_text(f"Укажите число: {new_value}", reply_markup=get_keyboard_fab())


callback_numbers = CallbackData("fabnum", "action")


def get_keyboard_fab():
    buttons = [types.InlineKeyboardButton(text=">", callback_data=callback_numbers.new(action="decr")),
               types.InlineKeyboardButton(text="<", callback_data=callback_numbers.new(action="incr")),
               types.InlineKeyboardButton(text="=", callback_data=callback_numbers.new(action="finish"))]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_fab_1():
    buttons1 = [types.InlineKeyboardButton(text="Начать заново", callback_data=callback_numbers.new(action="continue")),
               types.InlineKeyboardButton(text="Завершить", callback_data=callback_numbers.new(action="end"))]
    keyboard1 = types.InlineKeyboardMarkup(row_width=1)
    keyboard1.add(*buttons1)
    return keyboard1


async def update_num_text_fab(message: types.Message, new_value: int, new_number: int):
    with suppress(MessageNotModified):
        await message.edit_text(f"ПОПЫТОК: {new_value},\nМОЁ ЧИСЛО: {new_number}", reply_markup=get_keyboard_fab())


def incre(user_data, user_number, high, low, user_value, call: types.CallbackQuery):
    h = user_data[call.from_user.id][1]
    global c
    global u
    global use
    user_data[call.from_user.id][1] = user_number - (high - low) // 2
    if user_data[call.from_user.id][1] != h:
        user_data[call.from_user.id][2] = low
        user_data[call.from_user.id][3] = high
        user_number = user_data[call.from_user.id][1]
        c = call.message
        u = user_value + 1
        use = user_number
        return True
    else:
        return False


def decre(user_data, user_number, high, low, user_value, call: types.CallbackQuery):
    h = user_data[call.from_user.id][1]
    global c
    global u
    global use
    user_data[call.from_user.id][1] = user_number + (high - low) // 2
    if user_data[call.from_user.id][1] != h:
        user_number = user_data[call.from_user.id][1]
        user_data[call.from_user.id][2] = low
        user_data[call.from_user.id][3] = high
        c = call.message
        u = user_value + 1
        use = user_number
        return True
    else:
        return False


@dp.message_handler(commands="numbers_fab")
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = [0, 50_000_000, 0, 100_000_000]
    await message.answer("ПОПЫТОК: 0,\nМОЁ ЧИСЛО: 50000000", reply_markup=get_keyboard_fab())


@dp.callback_query_handler(callback_numbers.filter(action=["continue"]))
async def cmd_start_1(call: types.CallbackQuery):
    await call.message.edit_text('Набирай "/numbers_fab" и загадывай число.')
    await call.answer()


@dp.callback_query_handler(callback_numbers.filter(action=["end"]))
async def cmd_end_1(call: types.CallbackQuery):
    await call.message.edit_text('Пока👋. Не забывай про мои суперспособности:)')
    await call.answer()


async def update_num_mistake_fab(message: types.Message):
    with suppress(MessageNotModified):
        await message.edit_text("Произошла ошибка по одной из следующих причин:\n1) Вы забыли своё число\n2) Выбрали неверный знак\n3) Загадали число больше 100 миллионов, а я его угадать не могу 😔", reply_markup=get_keyboard_fab_1())


@dp.callback_query_handler(callback_numbers.filter(action=["incr", "decr"]))
async def callbacks_num_change_fab(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data[call.from_user.id][0]
    user_number = user_data[call.from_user.id][1]
    low = user_data[call.from_user.id][2]
    high = user_data[call.from_user.id][3]
    action = callback_data["action"]
    user_data[call.from_user.id][0] = user_value + 1
    if action == "incr":
        high = user_number
        if incre(user_data, user_number, high, low, user_value, call):
            await update_num_text_fab(c, u, use)
        else:
            await update_num_mistake_fab(c)
    elif action == "decr":
        low = user_number
        if decre(user_data, user_number, high, low, user_value, call):
            await update_num_text_fab(c, u, use)
        else:
            await update_num_mistake_fab(c)
    await call.answer()


def answer_to_user(number):
    p = number % 100
    ones = number % 10
    if 11 <= p <= 19:
        return 'ок'
    elif ones == 1:
        return 'ка'
    elif 2 <= ones <= 4:
        return 'ки'
    else:
        return 'ок'


@dp.callback_query_handler(callback_numbers.filter(action=["finish"]))
async def callbacks_num_finish_fab(call: types.CallbackQuery):
    number = int(user_data[call.from_user.id][0])
    await call.message.edit_text(f"Мне понадобилось {number} попыт" + str(answer_to_user(number)) + f".\nТы загадал {user_data[call.from_user.id][1]}.", reply_markup=get_keyboard_fab_1())
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp)
