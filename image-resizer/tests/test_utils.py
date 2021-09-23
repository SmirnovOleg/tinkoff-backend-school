from app.config import Size
from app.utils import ImageEncoder, resize_and_save_to_redis


def test_image_encoding(image_original_png, raw_encoded_image_original_png):
    assert (
        ImageEncoder.encode_image(image_original_png).decode()
        == raw_encoded_image_original_png
    )


def test_image_decoding(raw_encoded_image_original_png, image_original_png):
    assert (
        ImageEncoder.decode_image(raw_encoded_image_original_png) == image_original_png
    )


def test_resize_and_save_to_redis_func(fake_redis, encoded_image_original_png):
    task_id = '1'
    resize_and_save_to_redis(img_data=encoded_image_original_png, task_id=task_id)
    data = fake_redis.hgetall(task_id)

    assert data[Size.SIZE_ORIGINAL.encode()] == encoded_image_original_png.encode()
