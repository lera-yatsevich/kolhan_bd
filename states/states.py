from aiogram.filters.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния
    answ_name = State()        # Состояние ожидания ввода имени
    answ_test = State()        # Состояние ввода ответа на кодовый вопрос
    gift_1 = State()       # Подсказка по первому подарку
    gift_2 = State()       # Подсказка по второму подарку
    gift_3 = State()       # Подсказка по третьему подарку
    gift_4 = State()       # Подсказка по четвертому подарку
