import random
from contextlib import contextmanager
from decimal import Decimal
from time import sleep
from typing import Any, Dict, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PRICE_SCALE_FACTOR_IN_PERCENTS
from app.db.models import (
    CryptoCurrency,
    PredefinedTransactionTypes,
    TransactionType,
    User,
)
from app.exceptions import InvalidUsage

engine = create_engine('sqlite:///market.db', convert_unicode=True)
Session = sessionmaker(bind=engine)


def insert_initial_cryptocurrencies() -> None:
    with create_session() as session:
        if session.query(CryptoCurrency).count() == 0:
            session.bulk_save_objects(
                [
                    CryptoCurrency(
                        name='bitcoin',
                        purchase_price=Decimal('123.45'),
                        sale_price=Decimal('123.45'),
                    ),
                    CryptoCurrency(
                        name='ethereum',
                        purchase_price=Decimal('123.45'),
                        sale_price=Decimal('123.45'),
                    ),
                    CryptoCurrency(
                        name='dogecoin',
                        purchase_price=Decimal('123.45'),
                        sale_price=Decimal('123.45'),
                    ),
                    CryptoCurrency(
                        name='another_coin',
                        purchase_price=Decimal('123.45'),
                        sale_price=Decimal('123.45'),
                    ),
                    CryptoCurrency(
                        name='yet_another_coin',
                        purchase_price=Decimal('123.45'),
                        sale_price=Decimal('123.45'),
                    ),
                ]
            )
            session.bulk_save_objects(
                [
                    TransactionType(name=PredefinedTransactionTypes.BUY),
                    TransactionType(name=PredefinedTransactionTypes.SELL),
                ]
            )


def update_purchase_and_sale_prices() -> None:
    with create_session() as session:
        cryptocurrencies = session.query(CryptoCurrency).with_for_update().all()
        for crypto in cryptocurrencies:
            sale_factor = Decimal(
                random.randrange(
                    -PRICE_SCALE_FACTOR_IN_PERCENTS, PRICE_SCALE_FACTOR_IN_PERCENTS
                )
            )
            crypto.sale_price += crypto.sale_price * sale_factor / 100

            purchase_factor = Decimal(
                random.randrange(
                    -PRICE_SCALE_FACTOR_IN_PERCENTS, PRICE_SCALE_FACTOR_IN_PERCENTS
                )
            )
            crypto.purchase_price += crypto.purchase_price * purchase_factor / 100


def update_prices_permanently(delay_in_seconds: int) -> None:
    while True:
        try:
            update_purchase_and_sale_prices()
        except Exception:  # pylint: disable=broad-except
            continue
        sleep(delay_in_seconds)


def init_db() -> None:
    import app.db.models as models  # pylint: disable=import-outside-toplevel

    models.Base.metadata.create_all(engine)
    insert_initial_cryptocurrencies()


def teardown_db() -> None:
    import app.db.models as models  # pylint: disable=import-outside-toplevel

    models.Base.metadata.drop_all(engine)


@contextmanager
def create_session(**kwargs: Dict[str, Any]) -> Iterator[Any]:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def get_user_by_login(session: Any, login: str) -> Any:
    user = session.query(User).filter(User.login == login).first()
    if not user:
        raise InvalidUsage('User with specified login does not exist', status_code=404)
    return user
