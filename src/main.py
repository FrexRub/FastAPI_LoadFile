import warnings
from typing import Annotated
import logging

from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from src.core.config import COOKIE_NAME, configure_logging
from src.core.database import get_async_session
from src.core.jwt_utils import create_jwt, validate_password
from src.users.crud import (
    get_user_from_db,
)
from src.core.exceptions import (
    NotFindUser,
)
from src.users.models import User
from src.users.routers import router as router_users
from src.files.routers import router as router_files
from src.core.exceptions import ErrorInData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

description = """
    API Load File helps you do awesome stuff. 🚀

    You will be able to:

    * **Read users**
    * **Create/Update/Remove users**
    * **Load file**
"""


app = FastAPI(
    title="API_LoadFile",
    description=description,
    version="0.1.0",
    docs_url="/docs",
)

origins = ["http://localhost:8000", "http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_users)
app.include_router(router_files)


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


@app.post(
    "/token",
    response_class=JSONResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["main"],
)
async def login_for_access_token(
    data_login: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    try:
        user: User = await get_user_from_db(session=session, email=data_login.username)
    except NotFindUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with the username: {data_login.username} not found",
        )

    if await validate_password(
        password=data_login.password, hashed_password=user.hashed_password.encode()
    ):
        access_token: str = await create_jwt(str(user.id))

        resp = JSONResponse({"access_token": access_token, "token_type": "bearer"})
        resp.set_cookie(key=COOKIE_NAME, value=access_token, httponly=True)
        return resp
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error password for login: {data_login.username}",
        )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return HTMLResponse("<h2> Load files </h2>")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
