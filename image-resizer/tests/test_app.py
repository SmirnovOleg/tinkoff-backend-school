from fastapi import status

from app.config import JobStatus


def test_posting_original_png_image(client, encoded_image_original_png):
    resp = client.post(url='/tasks', json={'img_data': encoded_image_original_png})
    data = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert data['status'] == JobStatus.FINISHED


def test_posting_invalid_base64(client, encoded_image_original_png):
    resp = client.post(url='/tasks', json={'img_data': encoded_image_original_png[:-2]})
    data = resp.json()

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data == {
        'detail': [
            {
                'loc': ['body', 'img_data'],
                'msg': 'must be a valid base64-decoded image',
                'type': 'value_error',
            }
        ]
    }


def test_posting_jpeg_image(client, encoded_image_original_jpg):
    resp = client.post(url='/tasks', json={'img_data': encoded_image_original_jpg})
    data = resp.json()

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data == {
        'detail': [
            {
                'loc': ['body', 'img_data'],
                'msg': 'must be a PNG image',
                'type': 'value_error',
            }
        ]
    }


def test_posting_rectangle_image(client, encoded_image_rectangle_png):
    resp = client.post(url='/tasks', json={'img_data': encoded_image_rectangle_png})
    data = resp.json()

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data == {
        'detail': [
            {
                'loc': ['body', 'img_data'],
                'msg': 'must be a square image',
                'type': 'value_error',
            }
        ]
    }


def test_getting_task_status(client, queued_task_id):
    resp = client.get(url=f'/tasks/{queued_task_id}')
    data = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert data == {'task_id': queued_task_id, 'status': JobStatus.FINISHED}


def test_getting_resized_image_32(client, encoded_image_32_png, queued_task_id):
    resp = client.get(url=f'/tasks/{queued_task_id}/image?size=32')
    data = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert data == {
        'task_id': queued_task_id,
        'status': 'finished',
        'queried_size': '32',
        'resized_img_data': encoded_image_32_png,
    }


def test_getting_resized_image_64(client, encoded_image_64_png, queued_task_id):
    resp = client.get(url=f'/tasks/{queued_task_id}/image?size=64')
    data = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert data == {
        'task_id': queued_task_id,
        'status': 'finished',
        'queried_size': '64',
        'resized_img_data': encoded_image_64_png,
    }


def test_getting_resized_image_original(
    client, encoded_image_original_png, queued_task_id
):
    resp = client.get(url=f'/tasks/{queued_task_id}/image?size=original')
    data = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert data == {
        'task_id': queued_task_id,
        'status': 'finished',
        'queried_size': 'original',
        'resized_img_data': encoded_image_original_png,
    }
