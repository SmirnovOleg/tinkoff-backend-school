import base64
import time
from io import BytesIO
from typing import Any

from PIL import Image

from app.config import Size, redis_conn


class ImageEncoder:
    @staticmethod
    def encode_image(image: Image) -> bytes:
        buffered = BytesIO()
        image.save(buffered, format='PNG')
        return base64.b64encode(buffered.getvalue())

    @staticmethod
    def decode_image(img_data: str) -> Any:
        return Image.open(BytesIO(base64.b64decode(img_data.encode())))


def generate_task_id() -> str:
    return str(int(time.monotonic() * (10 ** 9)))


def resize_and_save_to_redis(img_data: str, task_id: str) -> None:
    image = ImageEncoder.decode_image(img_data)
    resized = {Size.SIZE_ORIGINAL: img_data}

    image_32 = image.copy()
    image_32.thumbnail((32, 32))
    resized[Size.SIZE_32] = ImageEncoder.encode_image(image_32).decode()

    image_64 = image.copy()
    image_64.thumbnail((64, 64))
    resized[Size.SIZE_64] = ImageEncoder.encode_image(image_64).decode()

    redis_conn.hmset(task_id, resized)
