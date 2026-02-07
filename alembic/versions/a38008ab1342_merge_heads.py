"""merge heads

Revision ID: a38008ab1342
Revises: 3f4b9a2c1d7e, d2f4b6c1e8a1
Create Date: 2026-02-07 11:35:15.898584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a38008ab1342'
down_revision: Union[str, Sequence[str], None] = ('3f4b9a2c1d7e', 'd2f4b6c1e8a1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
