from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="payment")
