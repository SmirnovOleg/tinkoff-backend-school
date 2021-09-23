from enum import Enum

import redis
from pydantic import BaseSettings, RedisDsn
from rq import Queue


class Settings(BaseSettings):
    redis_url: RedisDsn = 'redis://localhost:6379'  # type: ignore


redis_conn = redis.from_url(Settings().redis_url)
redis_queue = Queue(connection=redis_conn)


class Size(str, Enum):
    SIZE_32 = '32'
    SIZE_64 = '64'
    SIZE_ORIGINAL = 'original'


class JobStatus(str, Enum):
    QUEUED = 'queued'
    IN_PROGRESS = 'started'
    FINISHED = 'finished'
    FAILED = 'failed'
