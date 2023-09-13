from aiogram.filters.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния
    answ_name = State()        # Состояние ожидания ввода имени
    answ_test = State()        # Состояние ввода ответа на кодовый вопрос
    gift_dog_food = State()       # Подсказка по вкусняшкам
    gift_dog_toy = State()       # Подсказка по игрушке
    gift_dog_delicacy = State()       # Подсказка по копыту
    gift_park = State()       # Подсказка по парку
    gift_alise = State()    # Подсказка по алисе
    gift_family = State()   # Подсказка по подарку от семьи
    finale = State()
