from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class LessonStatus:
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False)
    lesson_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=LessonStatus.SCHEDULED)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reminded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    student: Mapped["Student"] = relationship("Student", back_populates="lessons")
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="lesson", uselist=False)
