"""Vehicles

Revision ID: 06c473d2db8b
Revises: e3358310abf0
Create Date: 2025-12-17 12:43:15.167931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06c473d2db8b'
down_revision: Union[str, Sequence[str], None] = 'e3358310abf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # duplicate of 2e37c0074375; intentionally no-op
    pass

def downgrade() -> None:
    pass

