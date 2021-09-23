from decimal import Decimal
from enum import Enum

from sqlalchemy import TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config import SQLITE_DECIMAL_SCALE
from app.db.types import SqliteDecimal

Base: DeclarativeMeta = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    balance = Column(
        SqliteDecimal(2),
        CheckConstraint('balance >= 0'),
        nullable=False,
        default=Decimal('1000'),
    )
    portfolio = relationship('Portfolio')
    transactions = relationship('Transaction')


class CryptoCurrency(Base):
    __tablename__ = 'CryptoCurrency'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sale_price = Column(
        SqliteDecimal(SQLITE_DECIMAL_SCALE),
        CheckConstraint('sale_price >= 0'),
        nullable=False,
    )
    purchase_price = Column(
        SqliteDecimal(SQLITE_DECIMAL_SCALE),
        CheckConstraint('purchase_price >= 0'),
        nullable=False,
    )
    last_update = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Portfolio(Base):
    __tablename__ = 'Portfolio'
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    cryptocurrency_id = Column(
        Integer, ForeignKey('CryptoCurrency.id'), primary_key=True
    )
    amount = Column(
        SqliteDecimal(SQLITE_DECIMAL_SCALE),
        CheckConstraint('amount >= 0'),
        nullable=False,
    )
    cryptocurrency = relationship('CryptoCurrency')


class Transaction(Base):
    __tablename__ = 'Transaction'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    type_id = Column(Integer, ForeignKey('TransactionType.id'))
    cryptocurrency_id = Column(Integer, ForeignKey('CryptoCurrency.id'))
    amount = Column(
        'amount',
        SqliteDecimal(SQLITE_DECIMAL_SCALE),
        CheckConstraint('amount >= 0'),
        nullable=False,
    )
    transaction_type = relationship('TransactionType')
    cryptocurrency = relationship('CryptoCurrency')


class TransactionType(Base):
    __tablename__ = 'TransactionType'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PredefinedTransactionTypes(str, Enum):
    BUY = 'buy'
    SELL = 'sell'
