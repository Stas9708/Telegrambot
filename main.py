from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup,
                           InlineKeyboardButton, CallbackQuery)
from db import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import text
import utils
import datetime

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_choose_trainer = ReplyKeyboardMarkup(resize_keyboard=True)
kb_next = ReplyKeyboardMarkup(resize_keyboard=True)
kb_time = InlineKeyboardMarkup()
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
    entry_to_db = State()


class TrainerChangeInfo(StatesGroup):
    change_price = State()
    change_schedule = State()
    change_number = State()
    change_desc = State()
    change_photo = State()


@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    result = db.get_people(message.from_user['id'])
    if result is None:
        await message.answer("Виберіть що забажаєте)", reply_markup=kb_start)
    elif db.get_trainer(person_id=result['id'])['person_id'] == result['id']:
        await message.answer("Ви зарегестровані як тренер.\nДля того щоб подивитись функціонал тренера введіть - "
                             "/for_trainers!")
    else:
        await message.answer("Ну що ж підкачаємось?)", reply_markup=kb_choose_trainer)


@dp.message_handler(commands=["help"])
async def help_command(message: Message):
    await message.reply(text=text.HELP_COMMAND, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text in ["Потренуватись", "Потренувати"], commands=["trainer_reg"])
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


@dp.message_handler(commands=["for_trainers"])
async def for_trainers_command(message: Message):
    await message.answer(text=text.TRAINERS_COMMAND)


@dp.message_handler(commands=["change_price", "change_schedule", "change_number", "change_desc", "change_photo"])
async def trainer_command(message: Message):
    if message.text == "/change_price":
        await message.answer("Вкажіть нову ціну")
        await TrainerChangeInfo.change_price.set()
    elif message.text == "/change_schedule":
        await message.answer("напишіть новий час роботи.")
        await TrainerChangeInfo.change_schedule.set()
    elif message.text == "/change_number":
        await message.answer("Напишіть новий номер телефону.")
        await TrainerChangeInfo.change_number.set()
    elif message.text == "/change_desc":
        await message.answer("Напишіть нове резюме.")
        await TrainerChangeInfo.change_desc.set()
    else:
        await message.answer("Пришліть нове фото.")
        await TrainerChangeInfo.change_photo.set()


@dp.message_handler(state=TrainerChangeInfo.change_price)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(utils.get_trainer_id(message.from_user.id), "/change_price", message.text)
    await message.reply("Ціну замінено успішно!")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_schedule)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(utils.get_trainer_id(message.from_user.id), "/change_schedule", message.text)
    await message.reply("Час роботи замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_number)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(utils.get_trainer_id(message.from_user.id), "/change_number", message.text)
    await message.reply("Номер телефону, замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_desc)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(utils.get_trainer_id(message.from_user.id), "/change_desc", message.text)
    await message.reply("Резюме замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_photo)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(utils.get_trainer_id(message.from_user.id), "/change_photo",
                           message.photo[-1].file_id)
    await message.reply("Фото замінено успішно.")
    await state.finish()


@dp.message_handler(commands=["see_work_schedule"])
async def get_trainer_schedule(message: Message):
    data = db.get_schedule(utils.get_trainer_id(message.from_user.id))
    await message.answer(text=data)


@dp.message_handler(lambda message: message.text in ["Вибрати тренера", "/work_out"])
async def show_trainer(message: Message, state: FSMContext):
    await TrainerChoiceState.trainer_info.set()
    async with state.proxy() as data:
        data['count'] = 0
        result = db.get_trainers(data['count'], utils.get_trainer_id(message.from_user.id))
        data['count'] += 1
        desc = text.TRAINER_DESCRIPTION.format(result['name'], result['description'], result['schedule'],
                                               result['price'], result['phone_number'])
        await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=desc,
                             reply_markup=kb_next)
        data['trainer'] = result['person_id']
        data['schedule'] = result['schedule']
        data['name'] = result['name']


@dp.message_handler(lambda message: message.text == "next >", state=TrainerChoiceState.trainer_info)
async def trainer_pagination(message: Message, state: FSMContext):
    async with state.proxy() as data:
        result = db.get_trainers(data['count'], utils.get_trainer_id(message.from_user.id))
        data['count'] += 1
        desc = text.TRAINER_DESCRIPTION.format(result['name'], result['description'], result['schedule'],
                                               result['price'], result['phone_number'])
        await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=desc,
                             reply_markup=kb_next)

        data['trainer'] = result['person_id']
        data['schedule'] = result['schedule']
        data['name'] = result['name']


@dp.message_handler(lambda message: message.text == "Подобається", state=TrainerChoiceState.trainer_info)
async def reg_for_training(message: Message, state: FSMContext):
    days = utils.get_next_five_days()
    kb_days = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_days.add(*days)
    async with state.proxy() as data:
        await message.answer(f"Ви обрали тренера - {data['name']}.\nВиберіть день для тренування!",
                             reply_markup=kb_days)


@dp.message_handler(lambda message: message.text in utils.get_next_five_days(),
                    state=TrainerChoiceState.trainer_info)
async def timing(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
        time = utils.get_time_slots(data['schedule'], data['day'])
        for el in time:
            kb_time.add(InlineKeyboardButton(text=el, callback_data=el))
        if data['day'] == str(datetime.datetime.now().date()):
            await message.reply(text="Сьогодні залишився тільки такий час:", reply_markup=kb_time)
        else:
            await message.reply(text="Виберіть зручний для вас час.", reply_markup=kb_time)
        await TrainerChoiceState.next()


@dp.callback_query_handler(state=TrainerChoiceState.entry_to_db)
async def load_to_db(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        json_str = utils.get_data(data['day'], callback_query.data,
                                  db.get_people(callback_query.from_user.id)['name'])
        db.add_to_timetable(data['trainer'], json_str)
        await bot.send_message(callback_query.from_user.id,
                               text=f"Ви записані до: {data['name']}.\nНа {data['day']},"
                                    f" о {callback_query.data} годині.", reply_markup=ReplyKeyboardRemove())
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
