from aiogram.fsm.state import State, StatesGroup


class AddStudent(StatesGroup):
    name = State()
    price = State()
    weekday = State()
    time = State()
    confirm = State()
