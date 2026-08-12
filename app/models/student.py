from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    notify_before_minutes: Mapped[int] = mapped_column(default=60)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    tutor: Mapped["User"] = relationship("User", back_populates="students")
    schedules: Mapped[list["StudentSchedule"]] = relationship(
        "StudentSchedule", back_populates="student", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="student", cascade="all, delete-orphan")
