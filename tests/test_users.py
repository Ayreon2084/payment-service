"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_accounts(client: AsyncClient, auth_headers_user, test_account):
    """Test getting user's accounts."""
    response = await client.get("/users/me/accounts", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    account = data[0]
    assert account["id"] == test_account.id
    assert account["balance"] == 100000
    assert "balance_in_major_currency_unit" in account
    assert account["balance_in_major_currency_unit"] == 1000.0


@pytest.mark.asyncio
async def test_get_my_accounts_empty(client: AsyncClient, db_session):
    """Test getting accounts for user with no accounts."""
    from app.core.security import hash_password
    from app.infrastructure.db.models.user_model import User

    new_user = User(
        email="noaddress@example.com",
        hashed_password=hash_password("TestPass123!"),
        full_name="No Account User",
        is_admin=False,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    login_response = await client.post(
        "/auth/login", data={"username": new_user.email, "password": "TestPass123!"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/users/me/accounts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_my_payments(
    client: AsyncClient, auth_headers_user, test_user, test_account, db_session
):
    """Test getting user's payments."""
    from app.core.enums import PaymentStatus
    from app.infrastructure.db.models.payment_model import Payment

    payment = Payment(
        transaction_id="test-transaction-123",
        account_id=test_account.id,
        user_id=test_user.id,
        amount=5000,
        status=PaymentStatus.SUCCESS,
    )
    db_session.add(payment)
    await db_session.commit()

    response = await client.get("/users/me/payments", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    payment_data = data[0]
    assert payment_data["transaction_id"] == "test-transaction-123"
    assert payment_data["amount"] == 5000
    assert payment_data["status"] == PaymentStatus.SUCCESS.value


@pytest.mark.asyncio
async def test_get_my_payments_empty(client: AsyncClient, auth_headers_user):
    """Test getting payments for user with no payments."""
    response = await client.get("/users/me/payments", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
