

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("kot@pes.com", "kotopes", 200),
        ("kot@pes.com", "kot0pes", 409),
        ("abcde", "pesokot", 422),
    ],
)
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("test1@test1.com", "test1", 200),
        ("test2@test2.com", "test2", 200),
        ("abcde@example.com", "pesokot", 401),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code
