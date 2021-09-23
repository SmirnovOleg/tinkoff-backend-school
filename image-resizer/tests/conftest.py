# pylint: disable=redefined-outer-name

import base64
import pathlib
from io import BytesIO

import pytest
from fakeredis import FakeStrictRedis
from fastapi import FastAPI
from PIL import Image
from rq import Queue, Retry
from starlette.testclient import TestClient

from app.routers import tasks
from app.utils import ImageEncoder, generate_task_id, resize_and_save_to_redis

assets_path = pathlib.Path(__file__).parent.absolute() / 'assets'


@pytest.fixture
def client():
    test_app = FastAPI()
    test_app.include_router(tasks.router)
    with TestClient(test_app) as c:
        yield c


@pytest.fixture()
def fake_redis():
    return FakeStrictRedis()


@pytest.fixture()
def fake_queue(fake_redis):
    queue = Queue(is_async=False, connection=fake_redis)
    return queue


@pytest.fixture(autouse=True)
def mock_objects(fake_queue, fake_redis, mocker):
    mocker.patch('app.config.redis_conn', fake_redis)
    mocker.patch('app.utils.redis_conn', fake_redis)
    mocker.patch('app.config.redis_queue', fake_queue)
    mocker.patch('app.routers.tasks.redis_conn', fake_redis)
    mocker.patch('app.routers.tasks.redis_queue', fake_queue)


@pytest.fixture()
def queued_task_id(fake_queue, encoded_image_original_png):
    task_id = generate_task_id()
    fake_queue.enqueue(
        resize_and_save_to_redis,
        args=(encoded_image_original_png, task_id),
        job_id=task_id,
        retry=Retry(max=3),
    )
    return task_id


@pytest.fixture
def image_original_png():
    return Image.open(assets_path / 'image_original.png')


@pytest.fixture
def encoded_image_original_png(image_original_png):
    return ImageEncoder.encode_image(image_original_png).decode()


@pytest.fixture
def encoded_image_original_jpg():
    image = Image.open(assets_path / 'image_invalid.jpeg')
    buffered = BytesIO()
    image.save(buffered, format='JPEG')
    return base64.b64encode(buffered.getvalue()).decode()


@pytest.fixture
def encoded_image_32_png():
    image = Image.open(assets_path / 'image_32.png')
    return ImageEncoder.encode_image(image).decode()


@pytest.fixture
def encoded_image_64_png():
    image = Image.open(assets_path / 'image_64.png')
    return ImageEncoder.encode_image(image).decode()


@pytest.fixture
def encoded_image_rectangle_png():
    image = Image.open(assets_path / 'image_rectangle.png')
    return ImageEncoder.encode_image(image).decode()


@pytest.fixture
def raw_encoded_image_original_png():
    return (
        'iVBORw0KGgoAAAANSUhEUgAAAOEAAADhBAMAAADMnc9JAAAAMFBMVEX///8AAAClpaVhYWGhoaFlZWXV1'
        'dUkJCQICAgJCQkKCgoLCwsMDAwNDQ0ODg4PDw9ZsmuKAAAAsElEQVR4nO3cwQmDQBRFUSFYgARxGyUdpA'
        'GtIQu3LtJ/DVYwDMr8QcO527c4HbymkSRJ0j/0m4J6bwlx6aKaE+IYJr6IROI9xOH7KdmaF/vEeLI2Lz7'
        'Lig8ikUgkEolEIpFIJBKJRCKRSCQSiUQikUgkEolEIpFIJBKJRCKRSCQSiUQikUgkEolEIpFIJBKJRCKR'
        'SDwm1v9dqf8tExKRSLy+uISJc0Ks/xMoSZKke7UDW3RKJI/CJZ0AAAAASUVORK5CYII='
    )


@pytest.fixture
def encoded_temp_image_1():
    return
