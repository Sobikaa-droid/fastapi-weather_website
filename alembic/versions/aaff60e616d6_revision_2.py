"""revision 2

Revision ID: aaff60e616d6
Revises: 3689b7d053a9
Create Date: 2025-11-16 06:29:40.211995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaff60e616d6'
down_revision: Union[str, Sequence[str], None] = '3689b7d053a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
