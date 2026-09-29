from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    username = Column(
        String(100),
        nullable=False,
    )

    age = Column(
        Integer,
        nullable=False,
    )

    weight = Column(
        Float,
        nullable=False,
    )

    goal = Column(
        String(100),
        nullable=False,
    )

    intensity = Column(
        String(50),
        nullable=False,
    )

    original_plan = Column(
        Text,
        nullable=True,
    )

    updated_plan = Column(
        Text,
        nullable=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    nutrition_tip = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )