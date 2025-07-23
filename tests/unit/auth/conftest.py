from unittest.mock import AsyncMock

import pytest
from fastapi import Request, Response

from src.auth import AuthService
from src.users import User


@pytest.fixture()
def mock_auth_service():
    return AsyncMock(spec=AuthService)


@pytest.fixture()
def mock_request():
    return AsyncMock(spec=Request)


@pytest.fixture()
def mock_response():
    return AsyncMock(spec=Response)


@pytest.fixture()
def mock_user():
    return AsyncMock(spec=User)
