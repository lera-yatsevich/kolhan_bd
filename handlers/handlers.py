from aiogram import Dispatcher, F

from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, StateFilter, Command


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import RedisStorage, Redis

from states.states import FSMFillForm
from lexicon.lexicon import lexicon, GIFT, NAMES, SURNAME


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


# Этот хэндлер будет срабатывать на команду /end до конца
@dp.message(F.text.lower().in_(['/end']),
            ~StateFilter(FSMFillForm.gift_family))
async def process_end_command_not_end(message: Message):
    await message.answer(text=lexicon.get('end_wrong'))


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('/cansel'))
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать только в финальном состоянии
@dp.message(StateFilter(FSMFillForm.finale))
async def process_start_command_state(message: Message):
    await message.answer(text=lexicon.get('finale'))


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
    await state.set_state(FSMFillForm.gift_dog_food)
    photo = FSInputFile("files//pic1.jpg")
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
@dp.message(StateFilter(FSMFillForm.gift_dog_food),
            F.text.lower().in_(GIFT.get('dog_food')))
async def process_gift1_answ(message: Message, state: FSMContext):
    await state.update_data(gift_1=message.text)
    await message.reply(text=lexicon.get('gift_1_found'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_dog_toy)
    photo = FSInputFile("files//pic2.jpg")
    await message.answer_photo(photo, caption=lexicon.get('gift_2'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по первому подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_dog_food),
            ~F.text.lower().in_(GIFT.get('dog_food')))
async def warning_not_gift1_answ(message: Message):
    await message.reply(text=lexicon.get('gift_1_failed'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на вопрос о 2-ом подарке
# и переводить в состояние выдачи подсказок по третьему подарку
@dp.message(StateFilter(FSMFillForm.gift_dog_toy),
            F.text.lower().in_(GIFT.get('dog_toy')))
async def process_gift2_answ(message: Message, state: FSMContext):
    await state.update_data(gift_2=message.text)
    await message.reply(text=lexicon.get('gift_2_found'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_dog_delicacy)
    photo = FSInputFile("files//pic3.jpg")
    await message.answer_photo(photo, caption=lexicon.get('gift_3'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по 2-ому подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_dog_toy),
            ~F.text.lower().in_(GIFT.get('dog_toy')))
async def warning_not_gift2_answ(message: Message):
    await message.reply(text=lexicon.get('gift_2_failed'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на вопрос о 3-ем подарке
# и переводить в состояние выдачи подсказок по четвертому подарку
@dp.message(StateFilter(FSMFillForm.gift_dog_delicacy),
            F.text.lower().in_(GIFT.get('dog_delicacy')))
async def process_gift3_answ(message: Message, state: FSMContext):
    await state.update_data(gift_3=message.text)
    await message.reply(text=lexicon.get('gift_3_found'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_park)
    photo = FSInputFile("files//pic4.png")
    await message.answer_photo(photo, caption=lexicon.get('gift_4'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по 3-ему подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_dog_delicacy),
            ~F.text.lower().in_(GIFT.get('dog_delicacy')))
async def warning_not_gift3_answ(message: Message):
    await message.reply(text=lexicon.get('gift_3_failed'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на вопрос о 4-ом подарке
# и переводить в состояние выдачи подсказок по пятому подарку
@dp.message(StateFilter(FSMFillForm.gift_park),
            F.text.lower().in_(GIFT.get('park')))
async def process_gift4_answ(message: Message, state: FSMContext):
    await state.update_data(gift_4=message.text)
    ticket = FSInputFile("files//ticket.pdf")
    await message.reply_document(caption=lexicon.get('gift_4_found'),
                                 document=ticket)
    # await message.reply(text=lexicon.get('gift_4_found'), )
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_alise)
    photo = FSInputFile("files//pic5.jpg")
    await message.answer_photo(photo, caption=lexicon.get('gift_5'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по 4-ому подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_park),
            ~F.text.lower().in_(GIFT.get('park')))
async def warning_not_gift4_answ(message: Message):
    await message.reply(text=lexicon.get('gift_4_failed'))


# Этот хэндлер будет срабатывать, если введен
# корректный ответ на вопрос о 5-ом подарке
# и переводить в состояние выдачи подсказок по шестому подарку
@dp.message(StateFilter(FSMFillForm.gift_alise),
            F.text.lower().in_(GIFT.get('alise')))
async def process_gift5_answ(message: Message, state: FSMContext):
    await state.update_data(gift_5=message.text)
    await message.reply(text=lexicon.get('gift_5_found'))
    # Устанавливаем состояние ожидания ввода подарка
    await state.set_state(FSMFillForm.gift_family)
    photo = FSInputFile("files//pic6.jpg")
    await message.answer_photo(photo, caption=lexicon.get('gift_6'))


# Этот хэндлер будет срабатывать, если во время
# ввода ответа на вопрос по 5-ому подарку введено что-то некорректное
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.gift_alise),
            ~F.text.lower().in_(GIFT.get('alise')))
async def warning_not_gift5_answ(message: Message):
    await message.reply(text=lexicon.get('gift_5_failed'))


# Этот хэндлер будет срабатывать, если введен
# любой ответ на текст о 6-ом подарке, кроме /end
@dp.message(StateFilter(FSMFillForm.gift_family),
            ~F.text.lower().in_(['/end']))
async def process_gift6_answ(message: Message, state: FSMContext):
    await state.update_data(gift_6=message.text)
    await message.reply(text=lexicon.get('gift_6_answer'))


# Этот хэндлер будет срабатывать на команду /end в конце
@dp.message(F.text.lower().in_(['/end']),
            StateFilter(FSMFillForm.gift_family))
async def process_end_command_end(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('end_end'))
    await state.set_state(FSMFillForm.finale)


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message()
async def send_echo(message: Message):
    await message.reply(text='Mоя твоя не понимать')
