# database/models.py

from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, nullable=True)
    text = Column(String, nullable=True)
    coins = Column(Integer, default=0, nullable=False)
    message_id = Column(Integer, nullable=False)


class UserAction(Base):
    __tablename__ = 'user_actions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    last_action = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
