from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    reviews = relationship('Review')


class Film(Base):
    __tablename__ = 'Film'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    avg_score = Column(Float, CheckConstraint('0 <= avg_score AND avg_score <= 10'))
    total_scores = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)

    reviews = relationship('Review')


class Review(Base):
    __tablename__ = 'Review'

    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    film_id = Column(Integer, ForeignKey('Film.id'), primary_key=True)
    comment = Column(Text)
    score = Column(Integer, CheckConstraint('0 <= score <= 10'))

    user = relationship('User')
