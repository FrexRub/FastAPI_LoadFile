from typing import Annotated, Optional
from uuid import UUID

import jwt
from fastapi import Depends, status, Path, Request
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.config import COOKIE_NAME
from src.core.jwt_utils import decode_jwt
from src.users.crud import get_user_by_id
from src.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def current_user_authorization_cookie(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    cookie_token = request.cookies.get(COOKIE_NAME)

    if cookie_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    try:
        payload = await decode_jwt(cookie_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    id_user = UUID(payload["sub"])
    return await get_user_by_id(session=session, id_user=id_user)


async def current_superuser_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    cookie_token = request.cookies.get(COOKIE_NAME)

    if cookie_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    try:
        payload = await decode_jwt(cookie_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    id_user = UUID(payload["sub"])
    user: User = await get_user_by_id(session=session, id_user=id_user)

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not an administrator",
        )
    return user


async def user_by_id(
    id_user: Annotated[UUID, Path],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization_cookie),
) -> User:
    find_user: Optional[User] = await get_user_by_id(session=session, id_user=id_user)
    if find_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id_user} not found!",
        )
    if user.id == id_user or user.is_superuser:
        return find_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights",
        )
