from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.responses import StreamingResponse

from src import auth, db
import asyncio
import base64
import json
import binascii


authenticated_router = APIRouter()
public_router = APIRouter()

@public_router.get("/issue-key")
async def issue_key():
    id = auth.create_id()
    apikey = auth.create_token(id)
    return {"id": id, 'apikey': apikey}


@public_router.get("/{id}/latest")
async def latest(id: str):
    data = await db.get_latest(id)
    return {'data': data}

@public_router.get("/{id}/stream")
async def latest(id: str):
    async def gen():
        async for data in db.get_stream(id):
            yield json.dumps({'data':data}) + '\n'
            await asyncio.sleep(3)

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), headers=headers)


@authenticated_router.post("/{id}")
async def create(id: str, data: bytes = File(...)):
    try:
        image_data = base64.b64decode(data, validate=True)
    except binascii.Error:
        raise HTTPException(status_code=400, detail="data is not base64 encoded")

    await db.create(id, data)
