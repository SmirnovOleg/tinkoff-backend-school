from typing import List

from pydantic import BaseModel


class MessagesHistory(BaseModel):
    history: List[str] = []


class User(BaseModel):
    id: str
    login: str
