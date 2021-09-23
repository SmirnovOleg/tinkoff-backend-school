import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket
from starlette import status
from starlette.websockets import WebSocketDisconnect

from app.connections import manager
from app.dao import (
    get_login_by_user_id,
    get_messages_channel,
    load_messages_history,
    register_new_user,
    save_and_publish_message,
)
from app.schema import MessagesHistory, User

router = APIRouter()


@router.get('/messages', response_model=MessagesHistory)
async def get_messages_history() -> Any:
    history = await load_messages_history()
    return MessagesHistory(history=history)


@router.post('/users/{login}', status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(login: str) -> Any:
    client_id = await register_new_user(login)
    return User(id=client_id, login=login)


@router.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> Any:
    client_login = await get_login_by_user_id(client_id)
    await manager.connect(websocket)

    async def reader(ch: Any) -> None:
        while await ch.wait_message():
            msg = (await ch.get()).decode()
            await manager.broadcast(msg)

    try:
        channel = await get_messages_channel()
        asyncio.create_task(reader(channel))

        while True:
            message = await websocket.receive_text()
            text = f'{client_login}: {message}'
            await save_and_publish_message(text)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f'{client_login} left the chat')
