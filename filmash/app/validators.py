from enum import Enum

from pydantic import BaseModel, SecretStr, validator


class UserRequestBodyModel(BaseModel):
    login: str
    password: SecretStr

    @validator('login')
    def must_not_contain_space(cls, value: str) -> str:
        if ' ' in value:
            raise ValueError('must not contain spaces')
        return value

    @validator('login')
    def must_not_contain_colons(cls, value: str) -> str:
        if ':' in value:
            raise ValueError('must not contain colons')
        return value


class ScoreRequestBodyModel(BaseModel):
    score: int

    @validator('score')
    def score_must_be_from_zero_to_ten(cls, value: int) -> int:
        if not 0 <= value <= 10:
            raise ValueError('must be between 0 and 10')
        return value


class ReviewRequestBodyModel(BaseModel):
    comment: str

    @validator('comment')
    def review_can_not_be_empty(cls, value: str) -> str:
        if value.isspace() or value == '':
            raise ValueError('can not be empty')
        return value


class SortType(str, Enum):
    ASC = 'asc'
    DESC = 'desc'
