"""Tests for service layer."""

import pytest

from app.application.services.account_service import AccountService
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.core.enums import CurrencyEnum
from app.infrastructure.db.repositories.account_repo import AccountRepository
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.schemas.user import UserAdminUpdate, UserCreate


@pytest.mark.asyncio
async def test_account_service_create_account(db_session, test_user):
    """Test AccountService.create_account."""
    account_repo = AccountRepository(db_session)
    account_service = AccountService(account_repo)

    account = await account_service.create_account(test_user.id, CurrencyEnum.EUR)
    assert account.user_id == test_user.id
    assert account.currency == CurrencyEnum.EUR
    assert account.balance == 0


@pytest.mark.asyncio
async def test_account_service_get_account_by_id(db_session, test_account):
    """Test AccountService.get_account_by_id."""
    account_repo = AccountRepository(db_session)
    account_service = AccountService(account_repo)

    account = await account_service.get_account_by_id(test_account.id)
    assert account is not None
    assert account.id == test_account.id


@pytest.mark.asyncio
async def test_account_service_get_account_by_id_with_access_check(
    db_session, test_account, test_user
):
    """Test AccountService.get_account_by_id_with_access_check."""
    account_repo = AccountRepository(db_session)
    account_service = AccountService(account_repo)

    # As owner
    account = await account_service.get_account_by_id_with_access_check(
        test_account.id, test_user.id, False
    )
    assert account is not None

    # As admin
    account = await account_service.get_account_by_id_with_access_check(
        test_account.id, None, True
    )
    assert account is not None

    # As different user (should return None)
    account = await account_service.get_account_by_id_with_access_check(
        test_account.id, 99999, False
    )
    assert account is None


@pytest.mark.asyncio
async def test_user_service_register_user(db_session):
    """Test UserService.register_user."""
    user_repo = UserRepository(db_session)
    user_service = UserService(user_repo)

    user_data = UserCreate(
        email="serviceuser@example.com",
        password="ServiceUser123!",
        full_name="Service User",
    )

    user = await user_service.register_user(user_data)
    assert user.email == "serviceuser@example.com"
    assert user.full_name == "Service User"
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_user_service_get_user_with_accounts(db_session, test_user, test_account):
    """Test UserService.get_user_with_accounts."""
    user_repo = UserRepository(db_session)
    user_service = UserService(user_repo)

    # Get single user
    user = await user_service.get_user_with_accounts(test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert len(user.accounts) > 0

    # Get all users
    users = await user_service.get_user_with_accounts()
    assert isinstance(users, list)
    assert len(users) > 0


@pytest.mark.asyncio
async def test_user_service_update_user(db_session, test_user):
    """Test UserService.update_user."""
    user_repo = UserRepository(db_session)
    user_service = UserService(user_repo)

    update_data = UserAdminUpdate(full_name="Updated Name")
    updated_user = await user_service.update_user(test_user.id, update_data)
    assert updated_user.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_user_service_delete_user(db_session, test_user):
    """Test UserService.delete_user."""
    from app.infrastructure.db.repositories.account_repo import AccountRepository

    user_repo = UserRepository(db_session)
    account_repo = AccountRepository(db_session)
    user_service = UserService(user_repo)

    # Create user without balance
    user_data = UserCreate(
        email="todelete@example.com", password="DeleteUser123!", full_name="To Delete"
    )
    user = await user_service.register_user(user_data)

    result = await user_service.delete_user(user.id, account_repo)
    assert "message" in result

    # Verify user is soft deleted
    deleted_user = await user_repo.get_by_id(user.id)
    assert deleted_user.is_deleted is True


@pytest.mark.asyncio
async def test_auth_service_authenticate_user(db_session, test_user):
    """Test AuthService.authenticate_user."""
    auth_service = AuthService(db_session)

    # Valid credentials
    user = await auth_service.authenticate_user(test_user.email, "TestPass123!")
    assert user is not False
    assert user.email == test_user.email

    # Invalid password
    user = await auth_service.authenticate_user(test_user.email, "WrongPass123!")
    assert user is False

    # Invalid email
    user = await auth_service.authenticate_user(
        "nonexistent@example.com", "TestPass123!"
    )
    assert user is False


@pytest.mark.asyncio
async def test_auth_service_create_token(db_session, test_user):
    """Test AuthService.create_token_for_user."""
    from jose import jwt

    from app.core.config import settings

    auth_service = AuthService(db_session)
    token = auth_service.create_token_for_user(test_user.id)

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(test_user.id)
