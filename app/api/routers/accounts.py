"""Account router endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AccountServiceDep, CurrentUserDep
from app.schemas.account import AccountCreate, AccountRead

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    account_service: AccountServiceDep,
    user: CurrentUserDep,
):
    """Create a new account for authenticated user."""
    return await account_service.create_account(user.id, account_data.currency)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    account_service: AccountServiceDep,
    user: CurrentUserDep,
):
    """Get account by ID. Requires authentication."""
    account = await account_service.get_account_by_id_with_access_check(
        account_id, user.id, user.is_admin
    )
    if not account:
        raw_account = await account_service.get_account_by_id(account_id)
        if raw_account:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Account belongs to another user."
            )
        raise HTTPException(status_code=404, detail="Account not found")
    return account
