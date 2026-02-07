"""Remove vehicle sharing flag

Revision ID: d2f4b6c1e8a1
Revises: 96d01d448efa
Create Date: 2025-02-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2f4b6c1e8a1"
down_revision: Union[str, Sequence[str], None] = "96d01d448efa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("vehicles", "is_sharing_location")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "vehicles",
        sa.Column("is_sharing_location", sa.Boolean(), nullable=True),
    )
