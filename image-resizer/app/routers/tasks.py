from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query, status
from rq.job import Retry

from app.config import Size, redis_conn, redis_queue
from app.schema import ImageRequestBodyModel
from app.utils import generate_task_id, resize_and_save_to_redis

router = APIRouter()


@router.post('/tasks', status_code=status.HTTP_201_CREATED)
def post_image(body: ImageRequestBodyModel) -> Any:
    task_id = generate_task_id()
    job = redis_queue.enqueue(
        f=resize_and_save_to_redis,
        args=(body.img_data, task_id),
        job_id=task_id,
        retry=Retry(max=3),
    )

    return {'task_id': task_id, 'status': job.get_status()}


@router.get('/tasks/{task_id}')
def get_task_status(
    task_id: int = Path(..., title='The ID of the redis-queue task to get', ge=1)
) -> Any:
    job = redis_queue.fetch_job(str(task_id))
    if not job:
        raise HTTPException(
            detail='Task with specified id does not exist.',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {'task_id': job.id, 'status': job.get_status()}


@router.get('/tasks/{task_id}/image')
def get_resized_image(
    task_id: int = Path(..., title='The ID of the redis-queue task to get', ge=1),
    size: Size = Query(None),
) -> Any:
    job = redis_queue.fetch_job(str(task_id))
    if not job:
        raise HTTPException(
            detail='Task with specified id does not exist.',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    resized_img_data = redis_conn.hgetall(job.id)[size.encode()]

    return {
        'task_id': job.id,
        'status': job.get_status(),
        'queried_size': size,
        'resized_img_data': resized_img_data,
    }
