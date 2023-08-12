from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import command
import json
import utils

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_choose_trainer = ReplyKeyboardMarkup(resize_keyboard=True)
kb_next = ReplyKeyboardMarkup(resize_keyboard=True)
button_dict = {"registration_button": [kb_start.add(KeyboardButton("Потренуватись")),
                                       kb_start.add(KeyboardButton("Потренувати"))],
               "client_button": [kb_choose_trainer.add(KeyboardButton("Вибрати тренера")),
                                 kb_next.add(KeyboardButton("next >")), kb_next.add(KeyboardButton("Подобається"))]
               }


class TrainerRegStates(StatesGroup):
    trainer_name = State()
    trainer_description = State()
    trainer_photo = State()
    trainer_schedule = State()
    trainer_price = State()
    trainer_phone = State()


class PeopleStates(StatesGroup):
    people_name = State()


class TrainerChoiceState(StatesGroup):
    trainer_info = State()


def schedule_to_json(person_id, schedule):
    pass


@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    result = db.get_people(message.from_user['id'])
    if result is None:
        await message.answer("Виберіть що забажаєте)", reply_markup=kb_start)
    elif db.get_trainer(result['id'])['person_id'] == result['id']:
        await message.answer("Ви зарегестровані як тренер.\nДля того щоб подивитись функціонал тренера введіть - "
                             "/for_trainers!", reply_markup=kb_choose_trainer)
    else:
        await message.answer("Ну що ж підкачаємось?)", reply_markup=kb_choose_trainer)


@dp.message_handler(commands=["help"])
async def help_command(message: Message):
    await message.reply(text=command.HELP_COMMAND, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text in ["Потренуватись", "Потренувати"])
async def registration(message: Message):
    if message.text == "Потренуватись":
        await message.answer("Будь-ласка зарегеструйтесь!\nНапишіть своє ім'я та прізвище.",
                             reply_markup=ReplyKeyboardRemove())
        await PeopleStates.people_name.set()
    else:
        await message.answer("Будь-ласка зарегеструйтесь!\nНапишіть своє ім'я та прізвище.",
                             reply_markup=ReplyKeyboardRemove())
        await TrainerRegStates.trainer_name.set()


@dp.message_handler(state=TrainerRegStates.trainer_name)
async def load_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_name'] = message.text
    await message.answer(
        "Напишіть коротеньке резюме ~ (Стаж роботи 7 років, чепміон України по бодіблдінгу в категорії 100+ кг!)")
    await TrainerRegStates.next()


@dp.message_handler(state=TrainerRegStates.trainer_description)
async def load_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_description'] = message.text
    await message.answer("Пришліть своє фото.")
    await TrainerRegStates.next()


@dp.message_handler(content_types=["photo"], state=TrainerRegStates.trainer_photo)
async def load_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_photo'] = message.photo[-1].file_id
    await message.answer("Напишіть свій щоденний графік роботи. ~ (07:00 - 22:00)")
    await TrainerRegStates.next()


@dp.message_handler(state=TrainerRegStates.trainer_schedule)
async def load_schedule(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_schedule'] = str(message.text)
    await message.answer("Напишіть ціну за одне тренування!")
    await TrainerRegStates.next()


@dp.message_handler(state=TrainerRegStates.trainer_price)
async def load_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_price'] = int(message.text)
    await message.answer("Напишіть свій номер телефону. ~ (0637512980)")
    await TrainerRegStates.next()


@dp.message_handler(state=TrainerRegStates.trainer_phone)
async def load_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainer_phone'] = str(message.text)
    db.add_people(message.from_user['id'], data['trainer_name'])
    response = db.get_people(message.from_user['id'])
    db.add_trainer(response['id'], data['trainer_description'], data['trainer_photo'], data['trainer_price'],
                   data['trainer_schedule'], data['trainer_phone'])
    await message.answer("Регістрація пройшла успішно!")
    await state.finish()


@dp.message_handler(state=PeopleStates.people_name)
async def load_client_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["client_name"] = message.text
    db.add_people(message.from_user['id'], data["client_name"])
    await message.answer("Регістрація пройшла успішно!", reply_markup=kb_choose_trainer)
    await state.finish()


@dp.message_handler(lambda message: message.text == "Вибрати тренера")
async def show_trainer(message: Message, state: FSMContext):
    await TrainerChoiceState.trainer_info.set()
    async with state.proxy() as data:
        data['count'] = 0
        result = db.get_trainers(data['count'])
        data['count'] += 1
        text = (
            f"Мене звати {result['name']}.\nОсь мої заслуги: {result['description']}!\nМій щоденний графік роботи:"
            f" {result['schedule']}.\nЦіна одного тренування становить - {result['price']} грн, мій номер телефону - "
            f"{result['phone_number']}!\nЯкщо вам підходить цей тренер, натисніть 'Подобається'.\n"
            f"Якщо ви хочете подивитись інших тренерів, натисніть 'next >'.")
        await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=text,
                             reply_markup=kb_next)
        data['trainer'] = result['person_id']
        data['schedule'] = result['schedule']
        data['name'] = result['name']


@dp.message_handler(lambda message: message.text == "next >", state=TrainerChoiceState.trainer_info)
async def trainer_pagination(message: Message, state: FSMContext):
    async with state.proxy() as data:
        result = db.get_trainers(data['count'])
        data['count'] += 1
        text = (
            f"Мене звати {result['name']}.\nОсь мої заслуги: {result['description']}!\nМій щоденний графік роботи:"
            f" {result['schedule']}.\nЦіна одного тренування становить - {result['price']} грн, мій номер телефону - "
            f"{result['phone_number']}!\nЯкщо вам підходить цей тренер, натисніть 'Подобається'.\n"
            f"Якщо ви хочете подивитись інших тренерів, натисніть 'next >'.")
        await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=text,
                             reply_markup=kb_next)
        data['trainer'] = result['person_id']
        data['schedule'] = result['schedule']
        data['name'] = result['name']


@dp.message_handler(lambda message: message.text == "Подобається", state=TrainerChoiceState.trainer_info)
async def reg_for_training(message: Message, state: FSMContext):
    days = utils.five_days()
    kb_days = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_days.add(*days)
    async with state.proxy() as data:
        await message.answer(f"Ви обрали тренера - {data['name']}.\nВиберіть день для тренрування!",
                             reply_markup=kb_days)


@dp.message_handler(lambda message: message.text in utils.five_days(), state=TrainerChoiceState.trainer_info)
async def timing(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
        time = utils.hours(data['schedule'], data['day'])
        pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
