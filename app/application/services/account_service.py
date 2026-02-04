"""Account service for business logic related to account management."""
from app.core.enums import CurrencyEnum
from app.infrastructure.db.models.account_model import Account
from app.infrastructure.db.repositories.account_repo import AccountRepository


class AccountService:
    """Service for account management operations."""

    def __init__(self, account_repo: AccountRepository):
        self.repo = account_repo

    async def create_account(
        self, user_id: int, currency: CurrencyEnum = CurrencyEnum.USD
    ) -> Account:
        """Create a new account for a user.

        Args:
            user_id: ID of the user to create account for.
            currency: Currency type for the account. Default: USD.

        Returns:
            Created Account instance.
        """
        account = Account(user_id=user_id, balance=0, currency=currency)
        await self.repo.create(account)
        await self.repo.session.commit()
        await self.repo.session.refresh(account)
        return account

    async def get_account_by_id(
        self, account_id: int, user_id: int | None = None
    ) -> Account | None:
        """Get account by ID without access check.

        Args:
            account_id: ID of the account.
            user_id: Optional user ID (not used for access check here).

        Returns:
            Account instance if found, None otherwise.
        """
        return await self.repo.get_by_id(account_id)

    async def get_account_by_id_with_access_check(
        self, account_id: int, user_id: int | None, is_admin: bool
    ) -> Account | None:
        """Get account by ID with access control check.

        Args:
            account_id: ID of the account.
            user_id: Optional user ID for ownership verification.
            is_admin: Whether the user is an administrator.

        Returns:
            Account instance if found and access granted, None otherwise.
        """
        account = await self.repo.get_by_id(account_id)
        if not account:
            return None
        if not is_admin and user_id and account.user_id != user_id:
            return None
        return account

    async def get_user_accounts(self, user_id: int) -> list[Account]:
        """Get all accounts for a user.

        Args:
            user_id: ID of the user.

        Returns:
            List of Account instances for the user.
        """
        return await self.repo.get_by_user_id(user_id)

    async def delete_account(self, account_id: int, user_id: int | None = None) -> bool:
        """Delete an account (soft delete).

        Args:
            account_id: ID of the account to delete.
            user_id: Optional user ID to verify ownership.

        Returns:
            True if account was deleted, False otherwise.
        """
        account = await self.repo.get_by_id(account_id)
        if not account:
            return False
        if user_id and account.user_id != user_id:
            return False
        return await self.repo.delete(account_id)
