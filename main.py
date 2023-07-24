from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
db = Database()


kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
start_button_list = [kb_start.add(KeyboardButton("Регістрація як клієнт")),
                     kb_start.add(KeyboardButton("Регістрація як тренер"))]

HELP_COMMAND = """
/start - початок роботи 
/help - список команд 
"""


class TrainerStates(StatesGroup):

    name = State()
    description = State()
    photo = State()


@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    await message.answer(text="Будь ласка зарегеструйтесь!", reply_markup=kb_start)


@dp.message_handler(commands=["help"])
async def help_command(message: Message):
    await message.reply(text=HELP_COMMAND, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Регістрація як тренер")
async def trainer_registration(message: Message):
    await message.answer("Введіть будь-ласка ім'я і фамілію.")
    await TrainerStates.name.set()


@dp.message_handler(state=TrainerStates.name)
async def load_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer(
        "Напишіть коротеньке резюме ~ (Стаж роботи 7 років, чепміон України по бодіблдінгу в категорії 100+ кг!)")
    await TrainerStates.next()


@dp.message_handler(state=TrainerStates.description)
async def load_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.answer("Пришліть своє фото.")
    await TrainerStates.next()


@dp.message_handler(content_types=["photo"], state=TrainerStates.photo)
async def load_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    db.add_trainer(data['name'], data['description'], data['photo'])
    await message.answer("Регістрація пройшла успішно!")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
