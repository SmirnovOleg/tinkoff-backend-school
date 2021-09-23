import asyncio
from typing import Any

import aiohttp
from aioconsole import ainput, aprint
from starlette import status

from app.config import settings


async def receive_messages(websocket: Any) -> None:
    async for msg in websocket:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await aprint(msg.data)
        elif msg.type in (aiohttp.WSMsgType.CLOSED, msg.type == aiohttp.WSMsgType.ERROR):
            break


async def send_messages(websocket: Any) -> None:
    while True:
        msg = await ainput()
        await websocket.send_str(msg)


async def run_client(client_id: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f'{settings.server_url}/ws/{client_id}', autoclose=False) as websocket:
            await asyncio.gather(
                receive_messages(websocket),
                send_messages(websocket)
            )


async def create_new_user() -> str:
    login = await ainput('Your login: ')
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{settings.server_url}/users/{login}') as resp:
            assert resp.status == status.HTTP_201_CREATED
            json_data = await resp.json()
            return json_data['client_id']


async def load_messages_history() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.server_url}/messages') as resp:
            assert resp.status == status.HTTP_200_OK
            json_data = await resp.json()
            return json_data['messages_history']


def main() -> None:
    loop = asyncio.get_event_loop()
    client_id = loop.run_until_complete(create_new_user())

    history = loop.run_until_complete(load_messages_history())
    for message in history:
        print(message)

    loop.run_until_complete(run_client(client_id))


if __name__ == '__main__':
    main()
