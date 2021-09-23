from fastapi import FastAPI

from app.handlers import router
from app.redis import redis

app = FastAPI()
app.include_router(router=router)


@app.on_event('startup')
async def startup_event() -> None:
    await redis.init_cache()


@app.on_event('shutdown')
async def shutdown_event() -> None:
    await redis.close()
