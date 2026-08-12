from datetime import date, datetime, time, timedelta

import pytz


def parse_time(text: str) -> time | None:
    """Парсит время в форматах ЧЧ:ММ, ЧЧ.ММ, ЧЧ ММ."""
    text = text.strip().replace(" ", ":").replace(".", ":")
    try:
        return datetime.strptime(text, "%H:%M").time()
    except ValueError:
        return None


def parse_price(text: str) -> float | None:
    """Парсит цену, возвращает float или None."""
    text = text.strip().replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]

WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def get_weekday_name(weekday: int) -> str:
    return WEEKDAYS[weekday]


def get_next_lesson_datetime(weekday: int, lesson_time: time, timezone: str) -> datetime:
    """Возвращает ближайшую дату-время занятия в заданном часовом поясе."""
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    today = now.date()
    days_ahead = weekday - today.weekday()
    if days_ahead < 0 or (days_ahead == 0 and now.time() > lesson_time):
        days_ahead += 7
    lesson_date = today + timedelta(days=days_ahead)
    return tz.localize(datetime.combine(lesson_date, lesson_time))
