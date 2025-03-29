import logging

import aiohttp
from fastapi import APIRouter, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import setting_conn, configure_logging, oauth_yandex
from authlib.integrations.starlette_client import OAuthError
from src.core.exceptions import (
    ErrorInData,
    ExceptAuthentication,
    EmailInUse,
    UniqueViolationError,
)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_yandex_user_data(access_token):
    params = {"format": "json"}
    headers = {"Authorization": f"OAuth {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://login.yandex.ru/info", params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def get_access_token(request: Request):
    try:
        token = await oauth_yandex.yandex.authorize_access_token(request)
    except OAuthError as exp:
        logger.exception("Error authentication by Yandex.ID %s", exc_info=exp)
        raise ExceptAuthentication(detail=exp)

    return token
