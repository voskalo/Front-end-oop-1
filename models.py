from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Float, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

likes = Table(
    'likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    liked_movies: Mapped[list[Movie]] = relationship(
        secondary=likes,
        back_populates='liked_by'
    )

class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Базові поля (були раніше)
    movie_name = mapped_column(String, nullable=False)
    poster_path = mapped_column(String, nullable=True)   # відносний шлях /abc.jpg

    # Нові поля — всі nullable щоб не зламати існуючі записи в БД
    poster_url   = mapped_column(String,  nullable=True)  # повний URL на зображення
    overview     = mapped_column(String,  nullable=True)  # опис фільму
    release_date = mapped_column(String,  nullable=True)  # дата виходу "2024-11-26"
    vote_average = mapped_column(Float,   nullable=True)  # рейтинг 0.0–10.0

    liked_by: Mapped[list[User]] = relationship(
        secondary=likes,
        back_populates='liked_movies'
    )

class Friendship(Base):
    __tablename__ = 'user_friends'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)

    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    friend: Mapped["User"] = relationship("User", foreign_keys=[friend_id])
