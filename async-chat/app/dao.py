from typing import Any, List

from app.config import CHANNEL_NAME, MESSAGES_TO_KEEP
from app.redis import redis
from app.utils import generate_client_id


async def register_new_user(login: str) -> str:
    client_id = generate_client_id()
    await redis.set(client_id, login)
    return client_id


async def load_messages_history() -> List[str]:
    await redis.ltrim('messages_history', -MESSAGES_TO_KEEP, -1)
    history = await redis.lrange('messages_history', 0, -1)
    return history


async def get_login_by_user_id(client_id: str) -> str:
    return (await redis.get(client_id)).decode()


async def save_and_publish_message(message: str) -> None:
    await redis.rpush('messages_history', message)
    await redis.publish(CHANNEL_NAME, message)


async def get_messages_channel() -> Any:
    return await redis.subscribe(CHANNEL_NAME)
