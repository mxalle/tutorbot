from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tutor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_time: Mapped[DateTime] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    notify_before_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    tutor: Mapped["User"] = relationship("User", back_populates="students")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="student", cascade="all, delete-orphan")
