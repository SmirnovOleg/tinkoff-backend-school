# pylint: disable=redefined-outer-name

import pytest

from app import create_app
from app.db.models import CryptoCurrency, User
from app.db.utils import create_session, init_db, teardown_db


@pytest.fixture()
def app():
    return create_app(should_init_db=False)


@pytest.fixture()
def client(app):
    app.config['TESTING'] = True
    app.worker.terminate()
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def __teardown_db_for_each_test():
    init_db()
    yield
    teardown_db()


@pytest.fixture()
def session():
    with create_session() as session:
        yield session


@pytest.fixture()
def user(session):
    new_user = User(login='user')
    session.add(new_user)
    session.commit()
    return new_user


@pytest.fixture()
def bitcoin(session):
    return (
        session.query(CryptoCurrency).filter(CryptoCurrency.name == 'bitcoin').first()
    )


@pytest.fixture()
def buy_two_bitcoins(client, user):
    return client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name='bitcoin', amount=2),
        follow_redirects=True,
    )


@pytest.fixture()
def buy_three_different_crypto(client, user):
    client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name='bitcoin', amount=1),
        follow_redirects=True,
    )
    client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name='ethereum', amount=1),
        follow_redirects=True,
    )
    client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name='dogecoin', amount=1),
        follow_redirects=True,
    )
