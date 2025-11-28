from datetime import datetime

from sqlalchemy import (
    CheckConstraint, Column, DateTime, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import declared_attr

from app.database import Base


class Review(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default='yandex')
    author_name = Column(String, nullable=False)
    rating = Column(
        Integer,
        CheckConstraint('rating >= 1 AND rating <= 5'), nullable=True
    )
    date_original = Column(DateTime, nullable=True)
    date_custom = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    avatar_filename = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    parsed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            'author_name', 'date_original',
            'text', name='reviews_unique'
        ),
    )
