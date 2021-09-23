from typing import Any

from flask import Blueprint, jsonify
from flask_pydantic import validate

from app.config import TRANSACTIONS_PER_PAGE
from app.db.models import Transaction, User
from app.db.utils import create_session, get_user_by_login
from app.exceptions import InvalidUsage
from app.pydantic_models import LoginRequestBodyModel, PaginationQueryModel

users = Blueprint('users', __name__, url_prefix='/users')


@users.route('/', methods=['POST'])
@validate()
def register_new_user(body: LoginRequestBodyModel) -> Any:
    login = body.login

    with create_session() as session:
        user = session.query(User).filter(User.login == login).first()
        if user:
            raise InvalidUsage('User with specified login already exists')
        user = User(login=login)
        session.add(user)
        registered_login = user.login
        session.flush()
        balance = user.balance

    return jsonify({'login': registered_login, 'balance': balance})


@users.route('/<string:login>/balance', methods=['GET'])
def get_balance(login: str) -> Any:
    with create_session() as session:
        user = get_user_by_login(session, login)
        balance = user.balance

    return jsonify({'login': login, 'balance': balance})


@users.route('/<string:login>/portfolio')
def get_portfolio(login: str) -> Any:
    with create_session() as session:
        user = get_user_by_login(session, login)
        user_cryptocurrencies = user.portfolio
        portfolio = []
        for record in user_cryptocurrencies:
            portfolio.append(
                {'cryptocurrency': record.cryptocurrency.name, 'amount': record.amount}
            )

    return jsonify({'login': login, 'portfolio': portfolio})


@users.route('/<string:login>/history', methods=['GET'])
@validate()
def get_transactions_history(login: str, query: PaginationQueryModel) -> Any:
    page = query.page - 1

    with create_session() as session:
        user = get_user_by_login(session, login)
        transactions = (
            session.query(Transaction)
            .filter(
                Transaction.user_id == user.id,
                Transaction.id > page * TRANSACTIONS_PER_PAGE,
            )
            .limit(TRANSACTIONS_PER_PAGE)
            .all()
        )

        history = []
        for transaction in transactions:
            history.append(
                {
                    'crypto_name': transaction.cryptocurrency.name,
                    'operation_type': transaction.transaction_type.name,
                    'amount': transaction.amount,
                }
            )

        total_transactions = (
            session.query(Transaction).filter(Transaction.user_id == user.id).count()
        )
        total_pages = (
            (total_transactions - 1) // TRANSACTIONS_PER_PAGE + 1
            if total_transactions != 0
            else 1
        )

        if page + 1 > total_pages:
            raise InvalidUsage(
                f'Page number = {page + 1} must be less than total number of pages = {total_pages}'
            )

    return jsonify(
        {
            'login': login,
            'history': history,
            'page_num': page + 1,
            'total_pages': total_pages,
        }
    )
