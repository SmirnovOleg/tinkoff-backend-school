from datetime import datetime
from typing import Any

from flask import Blueprint, jsonify
from flask_pydantic import validate

from app.db.models import (
    CryptoCurrency,
    Portfolio,
    PredefinedTransactionTypes,
    Transaction,
    TransactionType,
    User,
)
from app.db.utils import create_session, get_user_by_login
from app.exceptions import InvalidUsage
from app.pydantic_models import (
    CryptoTransactionRequestBodyModel,
    NewCryptoRequestBodyModel,
)

crypto = Blueprint('crypto', __name__, url_prefix='/cryptocurrencies')


@crypto.route('/<string:crypto_name>/prices', methods=['GET'])
def get_cryptocurrency_prices(crypto_name: str) -> Any:
    with create_session() as session:
        cryptocurrency = (
            session.query(CryptoCurrency)
            .filter(CryptoCurrency.name == crypto_name)
            .first()
        )
        if not cryptocurrency:
            raise InvalidUsage(
                'Cryptocurrency with specified name does not exist', status_code=404
            )
        sale_price = cryptocurrency.sale_price
        purchase_price = cryptocurrency.purchase_price

    return jsonify(
        {
            'crypto_name': crypto_name,
            'sale_price': sale_price,
            'purchase_price': purchase_price,
        }
    )


@crypto.route('/', methods=['POST'])
@validate()
def create_new_cryptocurrency(body: NewCryptoRequestBodyModel) -> Any:
    crypto_name = body.crypto_name
    sale_price = body.sale_price
    purchase_price = body.purchase_price

    with create_session() as session:
        if (
            session.query(CryptoCurrency)
            .filter(CryptoCurrency.name == crypto_name)
            .first()
        ):
            raise InvalidUsage('Cryptocurrency with specified name already exists')
        cryptocurrency = CryptoCurrency(
            name=crypto_name, sale_price=sale_price, purchase_price=purchase_price
        )
        session.add(cryptocurrency)
        registered_crypto_name = cryptocurrency.name
        registered_sale_price = cryptocurrency.sale_price
        registered_purchase_price = cryptocurrency.purchase_price

    return jsonify(
        {
            'crypto_name': registered_crypto_name,
            'sale_price': registered_sale_price,
            'purchase_price': registered_purchase_price,
        }
    )


@crypto.route('/buy', methods=['PUT'])
@validate()
def buy_cryptocurrency(body: CryptoTransactionRequestBodyModel) -> Any:
    utc_datetime = body.utc_datetime if body.utc_datetime else datetime.utcnow()
    login, crypto_name = body.login, body.crypto_name
    buy_amount = body.amount
    transaction_type_name = PredefinedTransactionTypes.BUY

    with create_session() as session:
        user = get_user_by_login(session, login)
        transaction_type = (
            session.query(TransactionType)
            .filter(TransactionType.name == transaction_type_name)
            .first()
        )
        cryptocurrency = (
            session.query(CryptoCurrency)
            .filter(CryptoCurrency.name == crypto_name)
            .first()
        )
        if not cryptocurrency:
            raise InvalidUsage(
                'Cryptocurrency with specified name does not exist', status_code=404
            )

        if cryptocurrency.last_update >= utc_datetime:
            raise InvalidUsage('Price of the specified cryptocurrency was updated')

        if user.balance < buy_amount * cryptocurrency.purchase_price:
            raise InvalidUsage("You don't have enough credits in the account")

        transaction = Transaction(
            amount=buy_amount,
            transaction_type=transaction_type,
            cryptocurrency=cryptocurrency,
        )
        user.balance -= buy_amount * cryptocurrency.purchase_price
        user.transactions.append(transaction)

        has_updated = False
        for record in user.portfolio:
            if record.cryptocurrency.name == crypto_name:
                record.amount += buy_amount
                has_updated = True
                break
        if not has_updated:
            user.portfolio.append(
                Portfolio(amount=buy_amount, cryptocurrency=cryptocurrency)
            )

        session.flush()
        transaction_id = transaction.id
        login = user.login

    return jsonify({'login': login, 'transaction_id': transaction_id})


@crypto.route('/sell', methods=['PUT'])
@validate()
def sell_cryptocurrency(body: CryptoTransactionRequestBodyModel) -> Any:
    utc_datetime = body.utc_datetime if body.utc_datetime else datetime.utcnow()
    login = body.login
    crypto_name = body.crypto_name
    sell_amount = body.amount
    transaction_type_name = PredefinedTransactionTypes.SELL

    with create_session() as session:
        user = session.query(User).filter(User.login == login).one()
        if not user:
            raise InvalidUsage(
                'User with specified login does not exist', status_code=404
            )
        transaction_type = (
            session.query(TransactionType)
            .filter(TransactionType.name == transaction_type_name)
            .one()
        )
        cryptocurrency = (
            session.query(CryptoCurrency)
            .filter(CryptoCurrency.name == crypto_name)
            .one()
        )
        if not cryptocurrency:
            raise InvalidUsage(
                'Cryptocurrency with specified name does not exist', status_code=404
            )

        if cryptocurrency.last_update >= utc_datetime:
            raise InvalidUsage('Price of the specified cryptocurrency was updated')

        performed_transaction = False
        for record in user.portfolio:
            if record.cryptocurrency.name == crypto_name:
                if record.amount < sell_amount:
                    raise InvalidUsage("You don't have enough crypto in your portfolio")
                transaction = Transaction(
                    amount=sell_amount,
                    transaction_type=transaction_type,
                    cryptocurrency=cryptocurrency,
                )
                record.amount -= sell_amount
                user.balance += sell_amount * cryptocurrency.sale_price
                user.transactions.append(transaction)

                session.flush()
                transaction_id = transaction.id
                performed_transaction = True
                break

        if not performed_transaction:
            raise InvalidUsage(
                "You don't have the specified cryptocurrency in your portfolio"
            )

    return jsonify({'login': login, 'transaction_id': transaction_id})
