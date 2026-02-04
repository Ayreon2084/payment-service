"""FastAPI dependencies for authentication and service DI."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.account_service import AccountService
from app.application.services.auth_service import AuthService
from app.application.services.payment_service import PaymentService
from app.application.services.user_service import UserService
from app.core.config import settings
from app.infrastructure.db.database import get_async_session
from app.infrastructure.db.models.user_model import User
from app.infrastructure.db.repositories.account_repo import AccountRepository
from app.infrastructure.db.repositories.payment_repo import PaymentRepository
from app.infrastructure.db.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        session: Database session dependency.
        token: JWT access token from Authorization header.

    Returns:
        User instance if authentication successful.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = UserRepository(session)
    user = await repo.get(int(user_id))
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_admin(current_user: CurrentUserDep) -> User:
    """Get current authenticated admin user.

    Args:
        current_user: Current authenticated user dependency.

    Returns:
        User instance if user is admin.

    Raises:
        HTTPException: If user is not an administrator.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentAdminDep = Annotated[User, Depends(get_current_admin)]


def get_user_service(session: SessionDep) -> UserService:
    """Create UserService instance with repository."""
    repo = UserRepository(session)
    return UserService(repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(session: SessionDep) -> AuthService:
    """Create AuthService instance with session."""
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_payment_service(session: SessionDep) -> "PaymentService":
    """Create PaymentService instance with required repositories."""
    payment_repo = PaymentRepository(session)
    account_repo = AccountRepository(session)
    user_repo = UserRepository(session)
    return PaymentService(session, payment_repo, account_repo, user_repo)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


def get_account_service(session: SessionDep) -> AccountService:
    """Create AccountService instance with repository."""
    account_repo = AccountRepository(session)
    return AccountService(account_repo)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def get_account_repository(session: SessionDep) -> AccountRepository:
    """Create AccountRepository instance."""
    return AccountRepository(session)


AccountRepositoryDep = Annotated[AccountRepository, Depends(get_account_repository)]
