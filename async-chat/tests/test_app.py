import asyncio

import pytest
from starlette import status

import app.dao
from app.utils import generate_client_id


@pytest.mark.asyncio
@pytest.mark.usefixtures('message_history')
async def test_get_messages_history(web_client, mocker):
    mocker.patch.object(app.dao, 'MESSAGES_TO_KEEP', 2)

    resp = await web_client.get('/messages')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {'history': ['Perfect', 'World']}


@pytest.mark.asyncio
async def test_create_user(web_client, first_user_login):
    resp = await web_client.post(f'/users/{first_user_login}')
    json_data = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert json_data['login'] == first_user_login
    assert json_data['id'].isdecimal()


@pytest.mark.asyncio
async def test_generate_client_id(loop):
    results = await asyncio.gather(
        loop.run_in_executor(None, generate_client_id),
        loop.run_in_executor(None, generate_client_id),
    )

    assert results[0] != results[1]
    assert results[0].isdecimal()
    assert results[1].isdecimal()


@pytest.mark.asyncio
async def test_websocket_endpoint_one_user(
    web_client, first_user_login, first_user_id, message
):
    async with web_client.websocket_connect(f'/ws/{first_user_id}') as websocket:
        await websocket.send_text(message)
        received_message = await websocket.receive_text()
        assert received_message == f'{first_user_login}: {message}'


@pytest.mark.asyncio
async def test_websocket_endpoint_two_users(
    web_client,
    first_user_login,
    second_user_login,
    first_user_id,
    second_user_id,
    message,
):  # pylint: disable=too-many-arguments
    async with web_client.websocket_connect(f'/ws/{first_user_id}') as websocket_1:
        async with web_client.websocket_connect(f'/ws/{second_user_id}') as websocket_2:
            await websocket_1.send_text(message)

            received_message_by_1 = await websocket_1.receive_text()
            assert received_message_by_1 == f'{first_user_login}: {message}'

            received_message_by_2 = await websocket_2.receive_text()
            assert received_message_by_2 == f'{first_user_login}: {message}'

        received_message_by_1 = await websocket_1.receive_text()
        assert received_message_by_1 == f'{second_user_login} left the chat'
