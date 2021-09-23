from decimal import Decimal
from typing import Any, Type

import sqlalchemy as sa
from flask.json import JSONEncoder
from sqlalchemy import TypeDecorator
from sqlalchemy.engine import Dialect


class SqliteDecimal(TypeDecorator):
    """https://stackoverflow.com/a/52526847

    This TypeDecorator use Sqlalchemy Integer as impl.
    It converts Decimals from Python to Integers which is later stored in Sqlite database.
    """

    impl = sa.Integer

    def __init__(self, scale: int) -> None:
        # It takes a 'scale' parameter, which specifies the number of digits
        # to the right of the decimal point of the number in the column.
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = 10 ** self.scale

    def process_bind_param(self, value: Any, dialect: Dialect) -> int:
        # e.g. value = Column(SqliteDecimal(2)) means a value such as
        # Decimal('12.34') will be converted to 1234 in Sqlite
        if value is not None:
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_literal_param(self, value: Any, dialect: Dialect) -> int:
        if value is not None:
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> Decimal:
        # e.g. Integer 1234 in Sqlite will be converted to Decimal('12.34'),
        # when query takes place.
        if value is not None:
            value = Decimal(value) / self.multiplier_int
        return value

    @property
    def python_type(self) -> Type[Decimal]:
        return Decimal


class DecimalJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> str:
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)
