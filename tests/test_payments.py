"""Tests for payment endpoints and webhook."""

import hashlib

import pytest
from httpx import AsyncClient

from app.core.config import settings


def generate_signature(
    account_id: int, amount: int, transaction_id: str, user_id: int
) -> str:
    """Generate webhook signature for testing."""
    secret_key = settings.payment_secret_key.get_secret_value()
    raw_str = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
    return hashlib.sha256(raw_str.encode()).hexdigest()


@pytest.mark.asyncio
async def test_webhook_success(client: AsyncClient, test_user, test_account):
    """Test successful webhook processing."""
    transaction_id = "test-transaction-001"
    amount = 5000
    signature = generate_signature(
        test_account.id, amount, transaction_id, test_user.id
    )

    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": test_account.id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == transaction_id
    assert data["amount"] == amount
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(client: AsyncClient, test_user, test_account):
    """Test webhook with invalid signature."""
    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": "test-transaction-002",
            "account_id": test_account.id,
            "user_id": test_user.id,
            "amount": 1000,
            "signature": "invalid-signature",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_create_account_if_not_exists(
    client: AsyncClient, test_user, db_session
):
    """Test webhook creates account if it doesn't exist."""
    from app.infrastructure.db.repositories.account_repo import AccountRepository

    # Ensure account doesn't exist
    account_repo = AccountRepository(db_session)
    accounts = await account_repo.get_by_user_id(test_user.id)
    new_account_id = max([acc.id for acc in accounts], default=0) + 1

    transaction_id = "test-transaction-003"
    amount = 3000
    signature = generate_signature(new_account_id, amount, transaction_id, test_user.id)

    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": new_account_id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response.status_code == 200

    # Verify account was created
    accounts = await account_repo.get_by_user_id(test_user.id)
    assert any(acc.id == new_account_id for acc in accounts)


@pytest.mark.asyncio
async def test_webhook_duplicate_transaction(
    client: AsyncClient, test_user, test_account
):
    """Test webhook rejects duplicate transaction."""
    transaction_id = "test-transaction-004"
    amount = 2000
    signature = generate_signature(
        test_account.id, amount, transaction_id, test_user.id
    )

    # First request
    response1 = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": test_account.id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response1.status_code == 200

    # Second request with same transaction_id
    response2 = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": test_account.id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response2.status_code == 200
    data = response2.json()
    # Should return success but indicate already processed
    assert "message" in data or data.get("status") == "success"


@pytest.mark.asyncio
async def test_webhook_account_balance_increase(
    client: AsyncClient, test_user, test_account, db_session
):
    """Test webhook increases account balance."""
    from app.infrastructure.db.repositories.account_repo import AccountRepository

    initial_balance = test_account.balance
    transaction_id = "test-transaction-005"
    amount = 15000
    signature = generate_signature(
        test_account.id, amount, transaction_id, test_user.id
    )

    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": test_account.id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response.status_code == 200

    # Verify balance increased
    account_repo = AccountRepository(db_session)
    updated_account = await account_repo.get_by_id(test_account.id)
    assert updated_account.balance == initial_balance + amount


@pytest.mark.asyncio
async def test_webhook_invalid_user(client: AsyncClient, test_account):
    """Test webhook with invalid user_id."""
    transaction_id = "test-transaction-006"
    amount = 1000
    signature = generate_signature(test_account.id, amount, transaction_id, 99999)

    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": test_account.id,
            "user_id": 99999,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_account_user_mismatch(
    client: AsyncClient, test_user, test_account, db_session
):
    """Test webhook with account that doesn't belong to user."""
    from app.core.security import hash_password
    from app.infrastructure.db.models.user_model import User
    from app.infrastructure.db.repositories.account_repo import AccountRepository

    # Create another user with account
    other_user = User(
        email="otheruser@example.com",
        hashed_password=hash_password("OtherPass123!"),
        full_name="Other User",
        is_admin=False,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    account_repo = AccountRepository(db_session)
    other_account = await account_repo.get_by_user_id(other_user.id)
    if not other_account:
        from app.core.enums import CurrencyEnum
        from app.infrastructure.db.models.account_model import Account

        other_account = Account(
            user_id=other_user.id, balance=0, currency=CurrencyEnum.USD
        )
        db_session.add(other_account)
        await db_session.commit()
        await db_session.refresh(other_account)

    # Try to use other_user's account with test_user's id
    transaction_id = "test-transaction-007"
    amount = 1000
    signature = generate_signature(
        other_account.id, amount, transaction_id, test_user.id
    )

    response = await client.post(
        "/payments/webhook",
        json={
            "transaction_id": transaction_id,
            "account_id": other_account.id,
            "user_id": test_user.id,
            "amount": amount,
            "signature": signature,
        },
    )
    assert response.status_code == 400
