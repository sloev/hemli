import jwt
import shortuuid
from fastapi import HTTPException

from src import settings


async def validate_access(id: str, apikey: str):
    try:
        jwt.decode(apikey, settings.SECRET_KEY, audience=id, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="apikey is invalid for this url")


def create_id():
    return shortuuid.uuid()


def create_token(id):
    payload = {"aud": id}
    token = jwt.encode(payload, settings.SECRET_KEY)
    return token
