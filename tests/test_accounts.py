"""Tests for account endpoints."""

import pytest
from httpx import AsyncClient

from app.core.enums import CurrencyEnum


@pytest.mark.asyncio
async def test_create_account_as_user(
    client: AsyncClient, auth_headers_user, test_user
):
    """Test creating account as regular user."""
    response = await client.post(
        "/accounts", json={"currency": "EUR"}, headers=auth_headers_user
    )
    assert response.status_code == 201
    data = response.json()
    assert data["currency"] == CurrencyEnum.EUR.value
    assert data["balance"] == 0
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_account_as_admin(
    client: AsyncClient, auth_headers_admin, test_admin
):
    """Test creating account as admin."""
    response = await client.post(
        "/accounts", json={"currency": "GBP"}, headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["currency"] == CurrencyEnum.GBP.value
    assert data["user_id"] == test_admin.id


@pytest.mark.asyncio
async def test_create_account_unauthorized(client: AsyncClient):
    """Test creating account without authentication."""
    response = await client.post("/accounts", json={"currency": "USD"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_account_as_owner(
    client: AsyncClient, auth_headers_user, test_account
):
    """Test getting account as owner."""
    response = await client.get(
        f"/accounts/{test_account.id}", headers=auth_headers_user
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_account.id
    assert data["balance"] == test_account.balance
    assert "balance_in_major_currency_unit" in data


@pytest.mark.asyncio
async def test_get_account_as_admin(
    client: AsyncClient, auth_headers_admin, test_account
):
    """Test getting account as admin."""
    response = await client.get(
        f"/accounts/{test_account.id}", headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_account.id


@pytest.mark.asyncio
async def test_get_account_unauthorized(client: AsyncClient, test_account):
    """Test getting account without authentication."""
    response = await client.get(f"/accounts/{test_account.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_account_not_found(client: AsyncClient, auth_headers_user):
    """Test getting non-existent account."""
    response = await client.get("/accounts/99999", headers=auth_headers_user)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_account_access_denied(
    client: AsyncClient, auth_headers_user, test_account, db_session
):
    """Test getting account that belongs to another user."""
    from app.core.security import hash_password
    from app.infrastructure.db.models.user_model import User

    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("OtherPass123!"),
        full_name="Other User",
        is_admin=False,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    # Try to access test_account as other_user
    login_response = await client.post(
        "/auth/login", data={"username": other_user.email, "password": "OtherPass123!"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/accounts/{test_account.id}", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
