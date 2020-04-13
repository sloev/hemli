from fastapi import APIRouter, File, HTTPException
from starlette.responses import StreamingResponse

from src import auth, db
import asyncio
import base64
import json
import binascii
import datetime

authenticated_router = APIRouter()
public_router = APIRouter()


@public_router.get("/health-check")
def healthcheck():
    return {"message": "ok"}


@public_router.get("/issue-key")
async def issue_key():
    hash_id = auth.create_hash_id()
    apikey = auth.create_token(hash_id)
    return {"hash_id": hash_id, "apikey": apikey}


@public_router.get("/{hash_id}/latest")
async def latest(hash_id: str):
    return await db.get_latest(hash_id)


@public_router.get("/{hash_id}/stream")
async def stream(hash_id: str, from_datetime: datetime.datetime = None):
    if from_datetime is None:
        from_datetime = datetime.datetime.now() - datetime.timedelta(days=2)

    async def gen():
        async for data in db.get_stream(hash_id, from_datetime):
            yield json.dumps({"data": data}) + "\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(gen(), headers=headers)


@authenticated_router.post("/{hash_id}")
async def create(hash_id: str, data: bytes = File(...)):
    # todo: add side-effect after response: get geoip and log stats
    try:
        image_data = base64.b64decode(data, validate=True)
    except binascii.Error:
        raise HTTPException(status_code=400, detail="data is not base64 encoded")

    await db.create(hash_id, data.decode("ascii"))
