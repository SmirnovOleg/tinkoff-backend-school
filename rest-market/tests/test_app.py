from decimal import Decimal

import pytest

import app.users
from app import config
from app.db.models import CryptoCurrency, PredefinedTransactionTypes
from app.db.utils import update_purchase_and_sale_prices


def test_register(client):
    resp = client.post('/users', json=dict(login='user'), follow_redirects=True)
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == 'user'
    assert json_data['balance'] == '1000'


def test_balance(client, user):
    resp = client.get(f'/users/{user.login}/balance', follow_redirects=True)
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['balance'] == '1000'


def test_prices_scale(bitcoin, session):
    old_sale_price = bitcoin.sale_price
    old_purchase_price = bitcoin.purchase_price

    update_purchase_and_sale_prices()
    session.commit()

    new_sale_price = bitcoin.sale_price
    new_purchase_price = bitcoin.purchase_price

    factor = Decimal(config.PRICE_SCALE_FACTOR_IN_PERCENTS / 100)
    assert (new_sale_price - old_sale_price) < Decimal(old_sale_price * factor)
    assert (new_purchase_price - old_purchase_price) < Decimal(
        old_purchase_price * factor
    )


def test_new_crypto(client, session):
    resp = client.post(
        '/cryptocurrencies',
        json=dict(crypto_name='testcoin', sale_price='100', purchase_price='101.23'),
        follow_redirects=True,
    )
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['crypto_name'] == 'testcoin'
    assert json_data['sale_price'] == '100'
    assert json_data['purchase_price'] == '101.23'

    new_crypto = (
        session.query(CryptoCurrency).filter(CryptoCurrency.name == 'testcoin').first()
    )
    assert new_crypto is not None
    assert new_crypto.sale_price == Decimal('100')
    assert new_crypto.purchase_price == Decimal('101.23')


def test_buying_crypto(client, user, session, bitcoin):
    resp = client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name=bitcoin.name, amount=1),
        follow_redirects=True,
    )
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == 'user'
    assert json_data['transaction_id'] == 1

    session.commit()

    assert len(user.portfolio) == 1
    assert user.portfolio[0].cryptocurrency.name == 'bitcoin'
    assert user.portfolio[0].amount == 1
    assert user.balance + bitcoin.purchase_price == Decimal('1000')


@pytest.mark.usefixtures('buy_three_different_crypto')
def test_buying_several_times(client, user):
    resp = client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name='bitcoin', amount=1),
        follow_redirects=True,
    )
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == user.login
    assert json_data['transaction_id'] == 4

    assert len(user.portfolio) == 3
    assert {it.cryptocurrency.name for it in user.portfolio} == {
        'bitcoin',
        'ethereum',
        'dogecoin',
    }
    assert sum([it.amount for it in user.portfolio]) == 4


def test_buying_crypto_with_insufficient_balance(client, user, bitcoin):
    resp = client.put(
        '/cryptocurrencies/buy',
        json=dict(login=user.login, crypto_name=bitcoin.name, amount=1000),
        follow_redirects=True,
    )

    assert resp.status_code == 400
    assert resp.get_json()['message'] == "You don't have enough credits in the account"


@pytest.mark.usefixtures('buy_three_different_crypto')
def test_requesting_portfolio(client, user):
    resp = client.get(f'/users/{user.login}/portfolio', follow_redirects=True)
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == user.login
    assert json_data['portfolio'] == [
        {'cryptocurrency': 'bitcoin', 'amount': '1'},
        {'cryptocurrency': 'ethereum', 'amount': '1'},
        {'cryptocurrency': 'dogecoin', 'amount': '1'},
    ]


@pytest.mark.usefixtures('buy_three_different_crypto')
def test_history_page_one(mocker, client, user):
    mocker.patch.object(app.users, 'TRANSACTIONS_PER_PAGE', 2)
    resp = client.get(f'/users/{user.login}/history?page=1', follow_redirects=True)
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == user.login
    assert json_data['history'] == [
        {
            'crypto_name': 'bitcoin',
            'operation_type': PredefinedTransactionTypes.BUY,
            'amount': '1',
        },
        {
            'crypto_name': 'ethereum',
            'operation_type': PredefinedTransactionTypes.BUY,
            'amount': '1',
        },
    ]
    assert json_data['page_num'] == 1
    assert json_data['total_pages'] == 2


@pytest.mark.usefixtures('buy_three_different_crypto')
def test_history_page_two(mocker, client, user):
    mocker.patch.object(app.users, 'TRANSACTIONS_PER_PAGE', 2)
    resp = client.get(f'/users/{user.login}/history?page=2', follow_redirects=True)
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == user.login
    assert json_data['history'] == [
        {
            'crypto_name': 'dogecoin',
            'operation_type': PredefinedTransactionTypes.BUY,
            'amount': '1',
        }
    ]
    assert json_data['page_num'] == 2
    assert json_data['total_pages'] == 2


@pytest.mark.usefixtures('buy_two_bitcoins')
def test_selling_crypto(client, session, user, bitcoin):
    resp = client.put(
        '/cryptocurrencies/sell',
        json=dict(login=user.login, crypto_name=bitcoin.name, amount=1),
        follow_redirects=True,
    )
    json_data = resp.get_json()

    assert resp.status_code == 200
    assert json_data['login'] == user.login
    assert json_data['transaction_id'] == 2

    session.commit()

    assert len(user.portfolio) == 1
    assert user.portfolio[0].cryptocurrency.name == bitcoin.name
    assert user.portfolio[0].amount == 1
    assert (
        user.balance
        == Decimal('1000') - 2 * bitcoin.purchase_price + bitcoin.sale_price
    )


@pytest.mark.usefixtures('buy_two_bitcoins')
def test_selling_crypto_with_insufficient_amount(client, user, bitcoin):
    resp = client.put(
        '/cryptocurrencies/sell',
        json=dict(login=user.login, crypto_name=bitcoin.name, amount=3),
        follow_redirects=True,
    )

    assert resp.status_code == 400
    assert (
        resp.get_json()['message'] == "You don't have enough crypto in your portfolio"
    )


@pytest.mark.usefixtures('buy_two_bitcoins')
def test_invalid_selling_without_specified_crypto(client, user):
    resp = client.put(
        '/cryptocurrencies/sell',
        json=dict(login=user.login, crypto_name='dogecoin', amount=3),
        follow_redirects=True,
    )

    assert resp.status_code == 400
    assert (
        resp.get_json()['message']
        == "You don't have the specified cryptocurrency in your portfolio"
    )


@pytest.mark.usefixtures('user')
def test_register_existing_user(client):
    resp = client.post('/users', json=dict(login='user'), follow_redirects=True)

    assert resp.status_code == 400
    assert resp.get_json()['message'] == 'User with specified login already exists'


def test_get_portfolio_from_nonexistent_user(client):
    resp = client.get('/users/ABC/portfolio', follow_redirects=True)

    assert resp.status_code == 404
    assert resp.get_json()['message'] == 'User with specified login does not exist'


def test_get_balance_from_nonexistent_user(client):
    resp = client.get('/users/ABC/balance', follow_redirects=True)

    assert resp.status_code == 404
    assert resp.get_json()['message'] == 'User with specified login does not exist'


def test_get_history_from_nonexistent_user(client):
    resp = client.get('/users/ABC/history?page=1', follow_redirects=True)

    assert resp.status_code == 404
    assert resp.get_json()['message'] == 'User with specified login does not exist'


def test_get_history_invalid_history_page(client, user):
    resp = client.get(f'/users/{user.login}/history?page=100', follow_redirects=True)

    assert resp.status_code == 400
    assert (
        resp.get_json()['message']
        == 'Page number = 100 must be less than total number of pages = 1'
    )


def test_nonexistent_crypto(client):
    resp = client.get('/cryptocurrencies/ABC/prices', follow_redirects=True)

    assert resp.status_code == 404
    assert (
        resp.get_json()['message']
        == 'Cryptocurrency with specified name does not exist'
    )
