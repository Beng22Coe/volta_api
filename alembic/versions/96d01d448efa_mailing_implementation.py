"""Mailing implementation

Revision ID: 96d01d448efa
Revises: 06c473d2db8b
Create Date: 2025-12-17 15:33:57.588329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96d01d448efa'
down_revision: Union[str, Sequence[str], None] = '06c473d2db8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # duplicate of e3358310abf0; intentionally no-op
    pass

def downgrade() -> None:
    pass
