import uvicorn

from fastapi import Depends, FastAPI, Header, HTTPException

from src.routes import authenticated_router, public_router

from src import settings, auth

app = FastAPI()


app.include_router(public_router)

app.include_router(
    authenticated_router,
    dependencies=[Depends(auth.validate_access)],
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9999, log_level='debug')
