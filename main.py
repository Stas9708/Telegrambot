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
import json

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_choose_trainer = ReplyKeyboardMarkup(resize_keyboard=True)
kb_next = ReplyKeyboardMarkup(resize_keyboard=True)
kb_days_of_week = ReplyKeyboardMarkup(resize_keyboard=True)
kb_entry = ReplyKeyboardMarkup(resize_keyboard=True)
kb_time = InlineKeyboardMarkup()
kb_date_for_trainer = InlineKeyboardMarkup()
kb_schedule = InlineKeyboardMarkup()
button_dict = {"registration_button": [kb_start.add(KeyboardButton("Потренуватись")),
                                       kb_start.add(KeyboardButton("Потренувати"))],
               "client_button": [kb_choose_trainer.add(KeyboardButton("Вибрати тренера")),
                                 kb_next.add(KeyboardButton("next >")),
                                 kb_next.add(KeyboardButton("Записатись на разове тренування")),
                                 kb_next.add(KeyboardButton("Записатись на постійній основі"))]
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


class TrainerScheduleState(StatesGroup):
    change_day = State()


class TrainerStandingScheduleState(StatesGroup):
    standing_schedule_info = State()


class CancelClientTrainingState(StatesGroup):
    client_name = State()
    date = State()
    time = State()


class CancelTrainerTrainingState(StatesGroup):
    date = State()
    time = State()


@dp.message_handler(commands=["start", "help"])
async def start_command(message: Message):
    if message.text == "/help":
        if db.get_trainer_id(message.from_user.id) is None:
            await message.reply(text=text.HELP_COMMAND, reply_markup=ReplyKeyboardRemove())
        else:
            await message.reply("Так як ви тренер, у вас зовсім інші команди.")
    else:
        result = db.get_people(message.from_user['id'])
        if result is None:
            await message.answer("Виберіть що забажаєте)", reply_markup=kb_start)
        elif db.get_trainer_id(message.from_user.id) == result['id']:
            await message.answer("Ви зарегестровані як тренер.\nДля того щоб подивитись функціонал тренера введіть - "
                                 "/for_trainers!", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Ну що ж підкачаємось?)", reply_markup=kb_choose_trainer)


@dp.message_handler(lambda message: message.text in ["Потренуватись", "Потренувати", "/trainer_reg"])
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
async def end_registration(message: Message, state: FSMContext):
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
    await message.answer("Регістрація пройшла успішно!\nДля того щоб подивитись функціонал тренера введіть - "
                         "/for_trainers!", reply_markup=kb_choose_trainer)
    await state.finish()


@dp.message_handler(commands=["change_price", "change_schedule", "change_number", "change_desc", "change_photo",
                              "for_trainers"])
async def trainer_command(message: Message):
    if message.text == "/for_trainers":
        await message.answer(text=text.TRAINERS_COMMAND, reply_markup=ReplyKeyboardRemove())
    elif message.text == "/change_price":
        await message.answer("Вкажіть нову ціну. Напишіть просто цифру!", reply_markup=ReplyKeyboardRemove())
        await TrainerChangeInfo.change_price.set()
    elif message.text == "/change_schedule":
        await message.answer("Напишіть новий час роботи ~ 07:00-21:00.", reply_markup=ReplyKeyboardRemove())
        await TrainerChangeInfo.change_schedule.set()
    elif message.text == "/change_number":
        await message.answer("Напишіть новий номер телефону.", reply_markup=ReplyKeyboardRemove())
        await TrainerChangeInfo.change_number.set()
    elif message.text == "/change_desc":
        await message.answer("Напишіть нове резюме.", reply_markup=ReplyKeyboardRemove())
        await TrainerChangeInfo.change_desc.set()
    elif message.text == "/change_photo":
        await message.answer("Пришліть нове фото.", reply_markup=ReplyKeyboardRemove())
        await TrainerChangeInfo.change_photo.set()
    else:
        await get_trainer_schedule(message)


@dp.message_handler(state=TrainerChangeInfo.change_price)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(db.get_trainer_id(message.from_user.id), "/change_price", message.text)
    await message.reply("Ціну замінено успішно!")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_schedule)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(db.get_trainer_id(message.from_user.id), "/change_schedule", message.text)
    await message.reply("Час роботи замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_number)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(db.get_trainer_id(message.from_user.id), "/change_number", message.text)
    await message.reply("Номер телефону, замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_desc)
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(db.get_trainer_id(message.from_user.id), "/change_desc", message.text)
    await message.reply("Резюме замінено успішно.")
    await state.finish()


@dp.message_handler(state=TrainerChangeInfo.change_photo, content_types=["photo"])
async def change_price_command(message: Message, state: FSMContext):
    db.change_trainer_info(db.get_trainer_id(message.from_user.id), "/change_photo",
                           message.photo[-1].file_id)
    await message.reply("Фото замінено успішно.")
    await state.finish()


@dp.message_handler(commands=["see_work_schedule"])
async def get_trainer_schedule(message: Message, state: FSMContext):
    await TrainerScheduleState.change_day.set()
    async with state.proxy() as data:
        data_dict = utils.get_general_dict(db.get_schedule(db.get_trainer_id(message.from_user.id)))
        data['general_dict'] = data_dict
        if data_dict is None:
            await message.answer("Нажаль у вас немає тренувань!")
        else:
            day_now = datetime.datetime.now().date()
            for key, value in data_dict.items():
                date_object = datetime.datetime.strptime(key, "%Y-%m-%d").date()
                if date_object >= day_now:
                    kb_date_for_trainer.add(InlineKeyboardButton(text=str(date_object), callback_data=str(date_object)))
            await message.answer("Виберіть день.", reply_markup=kb_date_for_trainer)


@dp.callback_query_handler(state=TrainerScheduleState.change_day)
async def show_trainer_schedule(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data_dict = data['general_dict']
        temp_str = ""
        for key, val in data_dict.items():
            if key == callback_query.data:
                for time, name in val.items():
                    if len(val) > 1:
                        temp_str += f"{time} - {name}\n"
                    else:
                        temp_str += f"{time} - {name}"
        await bot.send_message(chat_id=callback_query.from_user.id, text=temp_str)
        kb_date_for_trainer.inline_keyboard.clear()
    await state.finish()


@dp.message_handler(state=TrainerChoiceState.states, commands=["work_out"])
async def work_out_command_exception(message: Message, state: FSMContext):
    await message.reply("Щось пішло не так.")
    await start_command(message)
    await state.finish()


@dp.message_handler(lambda message: message.text in ["/work_out", "Вибрати тренера"])
async def show_trainer(message: Message, state: FSMContext):
    if message.text in text.CLIENT_COMMANDS_LIST and db.get_trainer_id(message.from_user.id) is None:
        if message.text in ["/start", "/help"]:
            await start_command(message)
        else:
            await registration(message)
    elif message.text in text.TRAINER_COMMANDS_LIST and type(db.get_trainer_id(message.from_user.id)) == int:
        if message.text == "/start":
            await start_command(message)
        else:
            await trainer_command(message)
    else:
        await TrainerChoiceState.trainer_info.set()
        async with state.proxy() as data:
            data['count'] = 0
            result = db.get_trainer_info(db.get_trainer_id(message.from_user.id), data['count'])
            if result is None:
                await message.answer("Нажаль, на данний момент тренерів немає!")
                await state.finish()
            else:
                data['count'] += 1
                desc = text.TRAINER_DESCRIPTION.format(result['name'], result['description'], result['schedule'],
                                                       result['price'], result['phone_number'])
                await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=desc,
                                     reply_markup=kb_next)
                data['trainer'] = result['person_id']
                data['schedule'] = result['schedule']
                data['name'] = result['name']


@dp.message_handler(lambda message: message.text in ["next >", *text.TRAINER_COMMANDS_LIST,
                                                     *text.CLIENT_COMMANDS_LIST], state=TrainerChoiceState.trainer_info)
async def trainer_pagination(message: Message, state: FSMContext):
    if message.text in text.CLIENT_COMMANDS_LIST and db.get_trainer_id(message.from_user.id) is None:
        if message.text in ["/start", "/help"]:
            await start_command(message)
        else:
            await registration(message)
        await state.finish()
    elif message.text in text.TRAINER_COMMANDS_LIST and type(db.get_trainer_id(message.from_user.id)) == int:
        if message.text == "/start":
            await start_command(message)
        else:
            await trainer_command(message)
        await state.finish()
    else:
        async with state.proxy() as data:
            result = db.get_trainer_info(db.get_trainer_id(message.from_user.id), data['count'])
            if result['photo'] is None:
                await message.answer("Нажаль тренерів більше немає.")
                await start_command(message)
            else:
                data['count'] += 1
                desc = text.TRAINER_DESCRIPTION.format(result['name'], result['description'], result['schedule'],
                                                       result['price'], result['phone_number'])
                await bot.send_photo(chat_id=message.from_user.id, photo=result['photo'], caption=desc,
                                     reply_markup=kb_next)

                data['trainer'] = result['person_id']
                data['schedule'] = result['schedule']
                data['name'] = result['name']


@dp.message_handler(lambda message: message.text == "Записатись на разове тренування",
                    state=TrainerChoiceState.trainer_info)
async def reg_for_training(message: Message, state: FSMContext):
    async with state.proxy() as data:
        days = utils.get_next_five_days()
        kb_days = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_days.add(*days)
        await message.answer(f"Ви обрали тренера - {data['name']}.\nВиберіть день для тренування!",
                             reply_markup=kb_days)


@dp.message_handler(lambda message: message.text in utils.get_next_five_days(),
                    state=TrainerChoiceState.trainer_info)
async def show_time_to_client(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
        time_slots = utils.get_time_slots(data['schedule'], data['day'])
        not_used_time_list = []
        schedule_dict = utils.get_general_dict(db.get_schedule(data['trainer']))
        data['general_dict'] = schedule_dict
        if schedule_dict:
            if data['day'] in schedule_dict.keys():
                for key, value in schedule_dict.items():
                    if key == data['day']:
                        for k in value.keys():
                            not_used_time_list.append(k)
        time_slots = time_slots + not_used_time_list
        for time in time_slots:
            if time_slots.count(time) == 1:
                kb_time.add(InlineKeyboardButton(text=time, callback_data=time))
        if data['day'] == str(datetime.datetime.now().date()):
            await message.reply(text="Сьогодні залишився тільки такий час:", reply_markup=kb_time)
        else:
            await message.reply(text="Виберіть зручний для вас час.", reply_markup=kb_time)
        await TrainerChoiceState.next()


@dp.callback_query_handler(state=TrainerChoiceState.entry_to_db)
async def load_to_db(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if data['day'] in data['general_dict'].keys():
            for key, value in data['general_dict'].items():
                if key == data['day']:
                    update_dict = {callback_query.data: db.get_people(callback_query.from_user.id)['name']}
                    temp = data['general_dict'].setdefault(key, {})
                    data['general_dict'][key] = temp | update_dict
        else:
            data['general_dict'] = data['general_dict'] | {data['day']: {callback_query.data:
                                                                             db.get_people(callback_query.from_user.id)[
                                                                                 'name']}}
        db.update_schedule(data['trainer'], data['general_dict'])
        await bot.send_message(callback_query.from_user.id,
                               text=f"Ви записані до: {data['name']}.\nНа {data['day']},"
                                    f" о {callback_query.data} годині.", reply_markup=ReplyKeyboardRemove())
    kb_time.inline_keyboard.clear()
    await state.finish()


@dp.message_handler(lambda message: message.text in ["Записатись на постійній основі"],
                    state=TrainerChoiceState.trainer_info)
async def show_days_of_week(message: Message, state: FSMContext):
    schedule = None
    trainer_id = None
    async with state.proxy() as data:
        schedule = data['schedule']
        trainer_id = data['trainer']
    await state.finish()
    await TrainerStandingScheduleState.standing_schedule_info.set()
    async with state.proxy() as data:
        data['trainer'] = trainer_id
        data['schedule'] = schedule
    for day in text.DAYS_OF_WEEK_DICT.values():
        kb_days_of_week.add(KeyboardButton(day))
    await message.answer("Виберіть дні для запису", reply_markup=kb_days_of_week)


@dp.message_handler(lambda message: message.text in [i[0]['text'] for i in kb_days_of_week.keyboard],
                    state=TrainerStandingScheduleState.standing_schedule_info)
async def change_days_for_standing_schedule(message: Message, state: FSMContext):
    if message.text == "Записатись":
        await change_standing_time(message, state)
    else:
        async with state.proxy() as data:
            if 'days' not in data.keys():
                data['days'] = []
                data['days'].append(message.text)
            else:
                data['days'].append(message.text)
            new_keyboard = []
            for el in kb_days_of_week.keyboard:
                if el[0]['text'] == "Записатись":
                    continue
                elif el[0]['text'] != message.text:
                    new_keyboard.append(el)
            kb_days_of_week.keyboard = new_keyboard
            kb_days_of_week.add(KeyboardButton("Записатись"))
            await message.answer(f"Якщо ви обрали достатньо днів, натисніть 'Записатись'",
                                 reply_markup=kb_days_of_week)


async def change_standing_time(message: Message, state: FSMContext):
    async with state.proxy() as data:
        kb_days_of_week.keyboard.clear()
        time_slots = utils.get_time_slots(data['schedule'])
        occupied_time_slots = db.get_schedule(data['trainer'])
        occupied_time_slots_list = []
        kb_time_slots = InlineKeyboardMarkup()
        if occupied_time_slots['standing_schedule']:
            occupied_dict = json.loads(occupied_time_slots['standing_schedule'])
            for key, value in occupied_dict.items():
                if key in data['days']:
                    for k in value.keys():
                        if k not in occupied_time_slots_list:
                            occupied_time_slots_list.append(k)

        for time in time_slots:
            if time not in occupied_time_slots_list:
                kb_time_slots.add(InlineKeyboardButton(text=time, callback_data=time))
        await message.answer("Виберіть час.", reply_markup=kb_time_slots)
        kb_time_slots.inline_keyboard.clear()


@dp.callback_query_handler(state=TrainerStandingScheduleState.standing_schedule_info)
async def load_standing_schedule_to_db(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        db.add_standing_schedule(data['trainer'], callback_query.data, data['days'],
                                 db.get_people(callback_query.from_user.id)['name'])
        await bot.send_message(callback_query.from_user.id, text=f"Ви записані о {callback_query.data}!\n"
                                                                 f"Ваші дні для тренувань - "
                                                                 f"{', '.join(data['days']).lower()}.",
                               reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=["cancel_workout", "cancel_training"])
async def start_cancel_training_for_client(message: Message, state: FSMContext):
    await CancelClientTrainingState.client_name.set()
    async with state.proxy() as data:
        data['client_name'] = db.get_people(message.from_user.id)['name']
        trainers_id = utils.get_trainers_id(data['client_name'], db.get_schedule())
        data['trainers_name'] = []
        for val in trainers_id:
            data['trainers_name'].append({val: db.get_trainer_name(val)['name']})

        kb_trainers = ReplyKeyboardMarkup(resize_keyboard=True)
        for el in data['trainers_name']:
            for name in el.values():
                kb_trainers.add(KeyboardButton(text=name))
        await message.answer(text="Виберіть тренера, у якого хочете відмінити тренування.", reply_markup=kb_trainers)
        kb_trainers.keyboard.clear()


@dp.message_handler(state=CancelClientTrainingState.client_name)
async def select_day_for_cancel_training(message: Message, state: FSMContext):
    async with state.proxy() as data:
        for el in data['trainers_name']:
            if message.text in el.values():
                data['trainers_name'] = el
                break
        data["general_dict"] = utils.get_general_dict(db.get_schedule(list(data['trainers_name'].keys())[0]))
        kb_date_for_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
        for key, value in data["general_dict"].items():
            if data['client_name'] in value.values():
                kb_date_for_cancel.add(KeyboardButton(text=key))
        await message.answer(text="Виберіть день для відміни тренування.", reply_markup=kb_date_for_cancel)
        await CancelClientTrainingState.next()
        kb_date_for_cancel.keyboard.clear()


@dp.message_handler(state=CancelClientTrainingState.date)
async def select_time_for_cancel_training(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
        kb_time_for_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
        for key, value in data["general_dict"].items():
            if key == message.text:
                if len(value) > 1:
                    for time in value.keys():
                        kb_time_for_cancel.add(KeyboardButton(text=time))
                else:
                    kb_time_for_cancel.add(KeyboardButton(text=list(value.keys())[0]))
        await message.answer(text="Виберіть час.", reply_markup=kb_time_for_cancel)
        await CancelClientTrainingState.next()
        kb_time_for_cancel.keyboard.clear()


@dp.message_handler(state=CancelClientTrainingState.time)
async def cancel_training_for_client(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if (data['day'] in data['general_dict'] and message.text in data['general_dict'][data['day']]
                and data['client_name'] in data['general_dict'][data['day']][message.text]):
            del data['general_dict'][data['day']][message.text]
        db.update_schedule(list(data['trainers_name'].keys())[0], data['general_dict'])
    await message.answer(text="Тренування відмінено!", reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['change_my_schedule'])
async def start_cancel_training_for_trainer(message: Message, state: FSMContext):
    await CancelTrainerTrainingState.date.set()
    async with state.proxy() as data:
        data['general_schedule'] = utils.get_general_dict(db.get_schedule(db.get_trainer_id(message.from_user.id)))
        kb_date_for_cancel = InlineKeyboardMarkup()
        if data['general_schedule']:
            for date in data['general_schedule'].keys():
                kb_date_for_cancel.add(InlineKeyboardButton(text=date, callback_data=date))
            await message.answer(text="Виберіть день!", reply_markup=kb_date_for_cancel)
            kb_date_for_cancel.inline_keyboard.clear()
        else:
            await message.answer(text="На даний момент, у вас немає тренувань!")
            await state.finish()


@dp.callback_query_handler(state=CancelTrainerTrainingState.date)
async def select_day_for_cancel_for_trainer(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['date'] = callback_query.data
        kb_time_for_cancel = InlineKeyboardMarkup()
        for date, value in data['general_schedule'].items():
            if date == data['date']:
                if len(value) > 1:
                    for key, val in value.items():
                        kb_time_for_cancel.add(InlineKeyboardButton(text=key + " - " + val,
                                                                    callback_data=key + " - " + val))
                else:
                    kb_time_for_cancel.add(
                        InlineKeyboardButton(text=list(value.keys())[0] + " - " + list(value.values())[0],
                                             callback_data=list(value.keys())[0] + " - " + list(value.values())[0]))
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Виберіть час і клієнта для відміни тренування!",
                               reply_markup=kb_time_for_cancel)
        await CancelTrainerTrainingState.next()
        kb_time_for_cancel.inline_keyboard.clear()


@dp.callback_query_handler(state=CancelTrainerTrainingState.time)
async def cancel_training_for_trainer(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        callback_list = callback_query.data.split(" - ")
        for key, val in data['general_schedule'].items():
            if key == data['date']:
                if len(val) > 1:
                    del data['general_schedule'][data['date']][callback_list[0]]
                    break
                else:
                    del data['general_schedule'][data['date']]
                    break
        db.update_schedule(db.get_trainer_id(callback_query.from_user.id), data['general_schedule'])
        await bot.send_message(chat_id=callback_query.from_user.id, text="Тренування відмінено успішно!")
        await bot.send_message(chat_id=db.get_people_chat_id(callback_list[1])['user_id'],
                               text=f"Тренер - "
                                    f"{db.get_trainer_name(db.get_trainer_id(callback_query.from_user.id))['name']}"
                                    f" відмінив ваше тренування {data['date']} о {callback_list[0]}!")
        await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
