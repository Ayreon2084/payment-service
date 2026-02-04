"""User service for business logic related to user management."""
from datetime import datetime, timezone

from app.core.security import hash_password
from app.infrastructure.db.models.user_model import User
from app.infrastructure.db.repositories.account_repo import AccountRepository
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.schemas.user import UserAdminCreate, UserAdminUpdate, UserCreate


class UserService:
    """Service for user management operations."""

    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def register_user(self, user_data: UserCreate | UserAdminCreate) -> User:
        """Register a new user.

        Args:
            user_data: User creation data (UserCreate or UserAdminCreate).
                       If UserAdminCreate, is_admin field will be taken into account.

        Returns:
            Created User instance.

        Raises:
            ValueError: If email is already registered.
        """
        if await self.repo.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        is_admin = getattr(user_data, "is_admin", False)

        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            is_admin=is_admin,
        )

        user = await self.repo.create(new_user)
        await self.repo.session.commit()
        await self.repo.session.refresh(user)
        return user

    async def update_user(self, user_id: int, user_in: UserAdminUpdate):
        """Update user information.

        Args:
            user_id: ID of the user to update.
            user_in: Update data with fields to modify.

        Returns:
            Updated User instance with accounts loaded.

        Raises:
            ValueError: If user not found.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        update_data = user_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.repo.session.commit()
        user_with_accounts = await self.repo.get_with_accounts(user_id)
        return user_with_accounts if user_with_accounts else user

    async def get_user_with_accounts(
        self, user_id: int | None = None
    ) -> list[User] | User | None:
        """Get user(s) with their accounts loaded.

        Args:
            user_id: Optional user ID. If None, returns all users.

        Returns:
            User instance if user_id provided, list of users otherwise.
            Returns None if user_id provided but user not found.
        """
        result = await self.repo.get_with_accounts(user_id)
        if not user_id:
            return result if isinstance(result, list) else []
        return result

    async def delete_user(self, user_id: int, account_repo: AccountRepository) -> dict:
        """Soft delete a user and their accounts.

        Args:
            user_id: ID of the user to delete.
            account_repo: Account repository for checking balances.

        Returns:
            Dictionary with success message.

        Raises:
            ValueError: If user not found or has accounts with positive balance.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        accounts = await account_repo.get_by_user_id(user_id)
        accounts_with_balance = [
            {"id": acc.id, "balance": acc.balance, "currency": acc.currency.value}
            for acc in accounts
            if acc.balance > 0
        ]

        if accounts_with_balance:
            total_balance = sum(acc["balance"] for acc in accounts_with_balance)
            raise ValueError(
                f"Cannot delete user. User has {len(accounts_with_balance)} account(s) "
                f"with total balance of {total_balance / 100:.2f} {accounts_with_balance[0]['currency']}. "
                f"Please withdraw before deletion. "
                f"Accounts: {[acc['id'] for acc in accounts_with_balance]}"
            )

        for account in accounts:
            account.is_deleted = True
            account.deleted_at = datetime.now(timezone.utc)

        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)

        await self.repo.session.commit()
        await self.repo.session.refresh(user)
        return {"message": "User deleted successfully"}
