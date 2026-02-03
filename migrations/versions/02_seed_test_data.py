"""seed_test_data

Revision ID: 02
Revises: 01
Create Date: 2026-02-02 10:31:34.432837

"""
from typing import Sequence, Union

from alembic import op
from passlib.context import CryptContext
import sqlalchemy as sa

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# revision identifiers, used by Alembic.
revision: str = '02'
down_revision: Union[str, Sequence[str], None] = '01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    admin_pass = pwd_context.hash(settings.seed_admin_password)
    user_pass = pwd_context.hash(settings.seed_user_password)

    user_table = sa.table(
        "users",
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("full_name", sa.String),
        sa.column("is_admin", sa.Boolean),
        sa.column("is_deleted", sa.Boolean),
    )

    op.bulk_insert(user_table, [
        {
            "email": settings.seed_admin_email, 
            "hashed_password": admin_pass, 
            "full_name": "Behold The Almighty Admin", 
            "is_admin": True,
            "is_deleted": False,
        },
        {
            "email": settings.seed_user_email, 
            "hashed_password": user_pass, 
            "full_name": "John Doe", 
            "is_admin": False,
            "is_deleted": False,
        },
    ])
    stmt = sa.text(
        "INSERT INTO accounts (user_id, balance, currency, is_deleted) "
        "SELECT id, 100000, 'USD', False FROM users WHERE email = :user_email"
    )
    op.execute(stmt.params(user_email=settings.seed_user_email))


def downgrade() -> None:
    """Downgrade schema."""
    stmt_acc = sa.text(
        "DELETE FROM accounts WHERE user_id IN ("
        "SELECT id FROM users WHERE email = :user_email)"
    )
    op.execute(stmt_acc.params(user_email=settings.seed_user_email))

    stmt_users = sa.text(
        "DELETE FROM users WHERE email IN (:admin_email, :user_email)"
    )
    op.execute(stmt_users.params(
        admin_email=settings.seed_admin_email, 
        user_email=settings.seed_user_email
    ))
