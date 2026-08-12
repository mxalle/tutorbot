from sqlalchemy import ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentSchedule(Base):
    __tablename__ = "student_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_time: Mapped[Time] = mapped_column(Time, nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="schedules")
