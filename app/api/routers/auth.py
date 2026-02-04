"""Authentication router endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthServiceDep, UserServiceDep
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):
    """Authenticate user and return JWT access token.

    Args:
        form_data: OAuth2 form data with username (email) and password.
        auth_service: Authentication service dependency.

    Returns:
        Dictionary with access_token and token_type.

    Raises:
        HTTPException: If credentials are invalid.
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = auth_service.create_token_for_user(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, user_service: UserServiceDep):
    """Register a new user account."""
    try:
        return await user_service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout():
    """Logout endpoint.

    Note: JWT tokens are stateless. Client should delete the token.
    This endpoint returns success for API consistency.
    """
    return {"detail": "Successfully logged out"}
