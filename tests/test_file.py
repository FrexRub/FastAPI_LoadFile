from httpx import AsyncClient
from pathlib import Path

import asyncio


async def test_unauthorized_access(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
):
    path_dir = Path(__file__).parent
    file_name = str(path_dir / "test_file.wav")

    files = {"upload_file": (file_name, open(file_name, "rb"), "multipart/form-data")}
    data = {"new_name_file": "new_test_file"}
    response = await client.post("/files/load", params=data, files=files)

    assert response.status_code == 401


async def test_load_no_name_file(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    path_dir = Path(__file__).parent
    file_name = str(path_dir / "test_file.wav")

    headers = {"Authorization": f"Bearer {token_admin}"}
    files = {"upload_file": (file_name, open(file_name, "rb"), "multipart/form-data")}
    data = {"new_name_file": None}
    response = await client.post(
        "/files/load", headers=headers, params=data, files=files
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The file name is not specified"}


async def test_load_file(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    path_dir = Path(__file__).parent
    file_name = str(path_dir / "test_file.wav")

    headers = {"Authorization": f"Bearer {token_admin}"}
    files = {"upload_file": (file_name, open(file_name, "rb"), "multipart/form-data")}
    data = {"new_name_file": "new_test_file"}
    response = await client.post(
        "/files/load", headers=headers, params=data, files=files
    )

    assert response.status_code == 200
    assert response.json() == {"response": "OK"}


async def test_load_duplicate_file(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    path_dir = Path(__file__).parent
    file_name = str(path_dir / "test_file.wav")

    headers = {"Authorization": f"Bearer {token_admin}"}
    files = {"upload_file": (file_name, open(file_name, "rb"), "multipart/form-data")}
    data = {"new_name_file": "new_test_file"}
    response = await client.post(
        "/files/load", headers=headers, params=data, files=files
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Duplicate name files"}
