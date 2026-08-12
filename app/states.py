from aiogram.fsm.state import State, StatesGroup


class AddStudent(StatesGroup):
    name = State()
    price = State()
    schedule_weekday = State()
    schedule_time = State()
    add_more_schedule = State()
    confirm = State()
