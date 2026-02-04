"""Tests for admin endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users_as_admin(
    client: AsyncClient, auth_headers_admin, test_user, test_admin
):
    """Test listing all users as admin."""
    response = await client.get("/admin/users", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    user_emails = [user["email"] for user in data]
    assert test_user.email in user_emails
    assert test_admin.email in user_emails


@pytest.mark.asyncio
async def test_list_users_as_user(client: AsyncClient, auth_headers_user):
    """Test listing users as regular user (should fail)."""
    response = await client.get("/admin/users", headers=auth_headers_user)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_detail_as_admin(
    client: AsyncClient, auth_headers_admin, test_user
):
    """Test getting user detail as admin."""
    response = await client.get(
        f"/admin/users/{test_user.id}", headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert "accounts" in data


@pytest.mark.asyncio
async def test_get_user_detail_not_found(client: AsyncClient, auth_headers_admin):
    """Test getting non-existent user detail."""
    response = await client.get("/admin/users/99999", headers=auth_headers_admin)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_as_admin(client: AsyncClient, auth_headers_admin):
    """Test creating user as admin."""
    response = await client.post(
        "/admin/users",
        json={
            "email": "newuser@example.com",
            "password": "NewUser123!",
            "full_name": "New User",
            "is_admin": False,
        },
        headers=auth_headers_admin,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_create_admin_user(client: AsyncClient, auth_headers_admin):
    """Test creating admin user."""
    response = await client.post(
        "/admin/users",
        json={
            "email": "newadmin@example.com",
            "password": "NewAdmin123!",
            "full_name": "New Admin",
            "is_admin": True,
        },
        headers=auth_headers_admin,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newadmin@example.com"
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_update_user_as_admin(client: AsyncClient, auth_headers_admin, test_user):
    """Test updating user as admin."""
    response = await client.patch(
        f"/admin/users/{test_user.id}",
        json={"full_name": "Updated Name", "email": "updated@example.com"},
        headers=auth_headers_admin,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_change_admin_status(
    client: AsyncClient, auth_headers_admin, test_user
):
    """Test updating user admin status."""
    response = await client.patch(
        f"/admin/users/{test_user.id}",
        json={"is_admin": True},
        headers=auth_headers_admin,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_delete_user_as_admin(
    client: AsyncClient, auth_headers_admin, test_user, db_session
):
    """Test deleting user as admin."""
    from app.core.security import hash_password
    from app.infrastructure.db.models.user_model import User

    user_to_delete = User(
        email="todelete@example.com",
        hashed_password=hash_password("DeletePass123!"),
        full_name="To Delete",
        is_admin=False,
    )
    db_session.add(user_to_delete)
    await db_session.commit()
    await db_session.refresh(user_to_delete)

    response = await client.delete(
        f"/admin/users/{user_to_delete.id}", headers=auth_headers_admin
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_with_balance(
    client: AsyncClient, auth_headers_admin, test_user, test_account
):
    """Test deleting user with balance (should fail)."""
    response = await client.delete(
        f"/admin/users/{test_user.id}", headers=auth_headers_admin
    )
    assert response.status_code == 400
    data = response.json()
    assert "balance" in data["detail"].lower() or "account" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_self_as_admin(
    client: AsyncClient, auth_headers_admin, test_admin
):
    """Test admin cannot delete themselves."""
    response = await client.delete(
        f"/admin/users/{test_admin.id}", headers=auth_headers_admin
    )
    assert response.status_code == 403
    data = response.json()
    assert (
        "yourself" in data["detail"].lower()
        or "delete yourself" in data["detail"].lower()
    )


@pytest.mark.asyncio
async def test_get_user_with_accounts(
    client: AsyncClient, auth_headers_admin, test_user, test_account
):
    """Test getting user with accounts."""
    response = await client.get(
        f"/admin/users/{test_user.id}", headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert isinstance(data["accounts"], list)
    assert len(data["accounts"]) > 0
    assert data["accounts"][0]["id"] == test_account.id
