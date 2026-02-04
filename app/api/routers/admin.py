"""Admin router for user management operations."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AccountRepositoryDep, CurrentAdminDep, UserServiceDep
from app.schemas.user import (
    UserAdminCreate,
    UserAdminReadWithAccounts,
    UserAdminUpdate,
    UserRead,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserAdminReadWithAccounts])
async def list_users(_admin: CurrentAdminDep, service: UserServiceDep):
    """Get list of all users with their accounts."""
    return await service.get_user_with_accounts()


@router.get("/users/{user_id}", response_model=UserAdminReadWithAccounts)
async def get_user_detail(
    user_id: int, _admin: CurrentAdminDep, service: UserServiceDep
):
    """Get user details with accounts by user ID."""
    user = await service.get_user_with_accounts(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    _admin: CurrentAdminDep, user_in: UserAdminCreate, service: UserServiceDep
):
    """Create new user by administrator."""
    try:
        return await service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/users/{user_id}", response_model=UserAdminReadWithAccounts)
async def update_user_by_admin(
    user_id: int,
    user_in: UserAdminUpdate,
    _admin: CurrentAdminDep,
    service: UserServiceDep,
):
    """Update user by administrator."""
    try:
        return await service.update_user(user_id, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(
    user_id: int,
    _admin: CurrentAdminDep,
    account_repo: AccountRepositoryDep,
    service: UserServiceDep,
):
    """Delete user by administrator (soft delete)."""
    if user_id == _admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete yourself"
        )
    try:
        await service.delete_user(user_id, account_repo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
