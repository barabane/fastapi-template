from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Response, status


@pytest.mark.asyncio
async def test_sign_up(mock_auth_service, mock_request, mock_response):
    from src.api.v1.auth import sign_up
    from src.auth.dtos import RegisterCredentialsDTO, TokenDTO

    credentials = RegisterCredentialsDTO(email="test@example.com", password="password")
    expected_token = TokenDTO(token="access", type="bearer")
    mock_auth_service.sign_up = AsyncMock(return_value=expected_token)

    result = await sign_up(mock_response, mock_request, credentials, mock_auth_service)

    mock_auth_service.sign_up.assert_called_once_with(
        mock_request, mock_response, credentials
    )
    assert result == expected_token


@pytest.mark.asyncio
async def test_send_code(mock_auth_service):
    from src.api.v1.auth import send_code

    email = "test@example.com"
    mock_auth_service.send_code = AsyncMock()

    await send_code(email, mock_auth_service)

    mock_auth_service.send_code.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_confirm_email(mock_auth_service):
    from src.api.v1.auth import confirm_email

    email = "test@example.com"
    code = 123456
    mock_auth_service.confirm_email = AsyncMock()

    await confirm_email(code, email, mock_auth_service)

    mock_auth_service.confirm_email.assert_called_once_with(email, code)


@pytest.mark.asyncio
async def test_sign_in_success(mock_auth_service, mock_request, mock_response):
    from src.api.v1.auth import sign_in
    from src.auth.dtos import LoginCredentialsDTO, TokenDTO

    credentials = LoginCredentialsDTO(email="test@example.com", password="password")
    expected_token = TokenDTO(token="access", type="bearer")
    mock_auth_service.login = AsyncMock(return_value=expected_token)
    mock_request.headers = {}

    result = await sign_in(mock_response, mock_request, credentials, mock_auth_service)

    mock_auth_service.login.assert_called_once_with(
        mock_request, mock_response, credentials
    )
    assert result == expected_token


@pytest.mark.asyncio
async def test_sign_in_already_logged_in(
    mock_auth_service, mock_request, mock_response
):
    from src.api.v1.auth import sign_in
    from src.auth.dtos import LoginCredentialsDTO

    credentials = LoginCredentialsDTO(email="test@example.com", password="password")
    mock_request.headers = {"Authorization": "Bearer some_token"}

    with pytest.raises(HTTPException) as exc_info:
        await sign_in(mock_response, mock_request, credentials, mock_auth_service)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Вы уже вошли"
    mock_auth_service.login.assert_not_called()


@pytest.mark.asyncio
async def test_logout(mock_auth_service, mock_user, mock_request, mock_response):
    from src.api.v1.auth import logout

    refresh_token = "some_refresh_token"
    mock_request.cookies = {"refresh_token": refresh_token}
    mock_auth_service.logout = AsyncMock()

    await logout(mock_request, mock_response, mock_user, mock_auth_service)

    mock_auth_service.logout.assert_called_once_with(refresh_token)
    mock_response.delete_cookie.assert_called_once_with("refresh_token")


@pytest.mark.asyncio
async def test_reset_password(mock_auth_service):
    from src.api.v1.auth import reset_password

    email = "test@example.com"
    mock_auth_service.send_reset_password_code = AsyncMock()

    await reset_password(email, mock_auth_service)

    mock_auth_service.send_reset_password_code.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_confirm_reset(mock_auth_service):
    from src.api.v1.auth import confirm_reset
    from src.auth.dtos import NewPasswordCredentialsDTO

    email = "test@example.com"
    code = 123456
    credentials = NewPasswordCredentialsDTO(
        new_password="new_password", repeat_new_password="new_password"
    )
    expected_response = Response()
    mock_auth_service.confirm_reset_password = AsyncMock(return_value=expected_response)

    result = await confirm_reset(code, credentials, email, mock_auth_service)

    mock_auth_service.confirm_reset_password.assert_called_once_with(
        email, code, credentials
    )
    assert result == expected_response


@pytest.mark.asyncio
async def test_update_password(mock_auth_service, mock_user):
    from src.api.v1.auth import update_password
    from src.auth.dtos import NewPasswordCredentialsDTO

    old_password = "old_password"
    credentials = NewPasswordCredentialsDTO(
        new_password="new_password", repeat_new_password="new_password"
    )
    expected_response = Response()
    mock_user.id = 1
    mock_auth_service.update_password = AsyncMock(return_value=expected_response)

    result = await update_password(
        old_password, credentials, mock_user, mock_auth_service
    )

    mock_auth_service.update_password.assert_called_once_with(
        mock_user.id, old_password, credentials
    )
    assert result == expected_response
