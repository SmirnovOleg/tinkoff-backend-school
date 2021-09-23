# pylint: disable=redefined-outer-name
import asyncio

import fakeredis.aioredis
import pytest
from async_asgi_testclient import TestClient

from app.main import app
from app.redis import redis


@pytest.fixture(autouse=True)
async def fake_redis(mocker):
    fake_redis_pool = await fakeredis.aioredis.create_redis_pool(
        server=fakeredis.FakeServer()
    )
    mocker.patch.object(redis, 'redis_cache', fake_redis_pool)
    yield
    await redis.close()


@pytest.fixture
@pytest.mark.usefixtures('fake_redis')
async def web_client():
    async with TestClient(app) as async_test_client:
        yield async_test_client


@pytest.fixture(scope='session')
def loop():
    return asyncio.get_event_loop()


@pytest.fixture
@pytest.mark.usefixtures('fake_redis')
async def message_history():
    await redis.rpush('messages_history', 'Hello')
    await redis.rpush('messages_history', 'Perfect')
    await redis.rpush('messages_history', 'World')


@pytest.fixture
def first_user_login():
    return 'Test login'


@pytest.fixture
def second_user_login():
    return 'Another test login'


@pytest.fixture
@pytest.mark.usefixtures('fake_redis')
async def first_user_id(first_user_login):
    client_id = '1'
    await redis.set(client_id, first_user_login)
    return client_id


@pytest.fixture
@pytest.mark.usefixtures('fake_redis')
async def second_user_id(second_user_login):
    client_id = '2'
    await redis.set(client_id, second_user_login)
    return client_id


@pytest.fixture
def message():
    return 'Hello!'
