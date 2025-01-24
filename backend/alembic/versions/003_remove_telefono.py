"""remove telefono field

Revision ID: 003_remove_telefono
Revises: 002_remove_email
Create Date: 2024-01-24 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_remove_telefono'
down_revision: Union[str, None] = '002_remove_email'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Eliminar la columna telefono
    op.drop_column('jugadores', 'telefono')

def downgrade() -> None:
    # Recrear la columna telefono
    op.add_column('jugadores', sa.Column('telefono', sa.String(), nullable=True)) 