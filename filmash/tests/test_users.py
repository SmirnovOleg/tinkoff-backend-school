import pytest


def test_registering_user(client):
    resp = client.post(url='/users', json={'login': 'user', 'password': '12345'})

    assert resp.status_code == 200
    assert resp.json()['registered_login'] == 'user'


@pytest.mark.usefixtures('user')
def test_registering_existing_user(client):
    resp = client.post(url='/users', json={'login': 'user', 'password': '12345'})

    assert resp.status_code == 409
    assert resp.json()['detail'] == 'User with specified login already exists'


def test_registering_user_login_with_colons(client):
    resp = client.post(
        url='/users', json={'login': 'user:hacker:haha', 'password': '12345'}
    )

    assert resp.status_code == 422
    assert resp.json()['detail'] == [
        {
            'loc': ['body', 'login'],
            'msg': 'must not contain colons',
            'type': 'value_error',
        }
    ]


def test_registering_user_login_with_spaces(client):
    resp = client.post(
        url='/users', json={'login': 'user   spaaaces ', 'password': '12345'}
    )

    assert resp.status_code == 422
    assert resp.json()['detail'] == [
        {
            'loc': ['body', 'login'],
            'msg': 'must not contain spaces',
            'type': 'value_error',
        }
    ]
