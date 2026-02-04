"""Pytest configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.enums import CurrencyEnum
from app.core.security import hash_password
from app.infrastructure.db.database import Base, get_async_session
from app.infrastructure.db.models.account_model import Account
from app.infrastructure.db.models.user_model import User
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = TestSessionLocal()
    try:
        yield session
        await session.rollback()
    finally:
        await session.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client with database override."""

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test User",
        is_admin=False,
        is_deleted=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123!"),
        full_name="Admin User",
        is_admin=True,
        is_deleted=False,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def test_account(db_session, test_user):
    """Create a test account for test_user."""
    account = Account(
        user_id=test_user.id,
        balance=100000,  # 1000.00 USD
        currency=CurrencyEnum.USD,
        is_deleted=False,
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def auth_headers_user(client, test_user):
    """Get authentication headers for test user."""
    response = await client.post(
        "/auth/login", data={"username": test_user.email, "password": "TestPass123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_admin(client, test_admin):
    """Get authentication headers for test admin."""
    response = await client.post(
        "/auth/login", data={"username": test_admin.email, "password": "AdminPass123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
