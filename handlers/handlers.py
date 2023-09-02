from aiogram import Dispatcher, F

from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, StateFilter, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import RedisStorage, Redis

from states.states import FSMFillForm
from lexicon.lexicon import lexicon, GIFT_1, GIFT_2, NAMES, SURNAME


redis: Redis = Redis(host='localhost')

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
storage: RedisStorage = RedisStorage(redis=redis)

dp: Dispatcher = Dispatcher(storage=storage)


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и переводит в состояние заполнения анкеты
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('/start'))
    await state.set_state(FSMFillForm.answ_name)
    await message.answer(lexicon.get('start_question'))


# Этот хэндлер будет срабатывать на команду /start вне состояний
@dp.message(CommandStart(), ~StateFilter(default_state))
async def process_start_command_state(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('start_if_started'))


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=lexicon.get('cansel_if_default'))


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('/cansel'))
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ответа на контрольный вопрос
@dp.message(StateFilter(FSMFillForm.answ_name),
            F.text.lower().in_(NAMES))
async def process_name_sent(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('control_1'))
    await state.update_data(name=message.text)
    # Устанавливаем состояние ожидания ввода ответа на контрольный вопрос
    await state.set_state(FSMFillForm.answ_test)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.answ_name),
            ~F.text.lower().in_(NAMES))
async def warning_not_name(message: Message):
    await message.reply(text=lexicon.get('wrong_name'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на контрольный вопрос
# и переводить в состояние выдачи подсказок по первому подарку
@dp.message(StateFilter(FSMFillForm.answ_test),
            F.text.lower() == SURNAME)
async def process_control_answ(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.reply(text=lexicon.get('correct_answer'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_1)
    photo = FSInputFile("hint_photos//pic1.jpeg")
    await message.answer_photo(photo, caption=lexicon.get('gift_1'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на контрольный вопрос введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.answ_test),
            F.text.lower() != SURNAME)
async def warning_not_control_answ(message: Message):
    await message.reply(
        text=lexicon.get('wrong_surname'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на вопрос о 1-ом подарке
# и переводить в состояние выдачи подсказок по второму подарку
@dp.message(StateFilter(FSMFillForm.gift_1),
            F.text.lower().in_(GIFT_1))
async def process_gift1_answ(message: Message, state: FSMContext):
    await state.update_data(gift_1=message.text)
    await message.reply(text=lexicon.get('gift_1_found'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_2)
    photo = FSInputFile("hint_photos//pic2.png")
    await message.answer_photo(photo, caption=lexicon.get('gift_2'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по первому подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_1),
            ~F.text.lower().in_(GIFT_1))
async def warning_not_gift1_answ(message: Message):
    await message.reply(text=lexicon.get('gift_1_failed'))


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message()
async def send_echo(message: Message):
    await message.reply(text='Mоя твоя не понимать')
