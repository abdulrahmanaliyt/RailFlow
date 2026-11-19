"""require expiry for held reservations

Revision ID: e0bb89046446
Revises: 229ca1123c62
Create Date: 2026-11-19 22:15:13.729316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0bb89046446'
down_revision: Union[str, Sequence[str], None] = '229ca1123c62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""require expiry for held reservations

Revision ID: e0bb89046446
Revises: 229ca1123c62
Create Date: 2026-11-19 22:15:13.729316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0bb89046446'
down_revision: Union[str, Sequence[str], None] = '229ca1123c62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "held_reservation_requires_expiry",
        "seat_segment_reservations",
        "status != 'HELD' OR expires_at IS NOT NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "held_reservation_requires_expiry",
        "seat_segment_reservations",
        type_="check",
    )