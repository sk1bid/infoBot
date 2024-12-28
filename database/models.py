
from sqlalchemy import (
    String, DateTime, func, Integer, Text,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column
)


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Media(Base):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer(), nullable=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    coins: Mapped[int] = mapped_column(Integer(), nullable=True)
