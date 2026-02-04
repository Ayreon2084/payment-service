"""User router endpoints for user-related operations."""
from fastapi import APIRouter

from app.api.deps import (
    AccountServiceDep,
    CurrentUserDep,
    PaymentServiceDep,
)
from app.schemas.account import AccountRead
from app.schemas.payment import PaymentRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def read_user_me(user: CurrentUserDep):
    """Get current authenticated user's information."""
    return user


@router.get("/me/accounts", response_model=list[AccountRead])
async def get_my_accounts(user: CurrentUserDep, account_service: AccountServiceDep):
    """Get all accounts for the current authenticated user."""
    return await account_service.get_user_accounts(user.id)


@router.get("/me/payments", response_model=list[PaymentRead])
async def get_my_payments(user: CurrentUserDep, payment_service: PaymentServiceDep):
    """Get all payments for the current authenticated user."""
    return await payment_service.get_user_payments(user.id)
