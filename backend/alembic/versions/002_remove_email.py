"""remove email field

Revision ID: 002_remove_email
Revises: 001_update_jugadores
Create Date: 2024-01-24 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_remove_email'
down_revision: Union[str, None] = '001_update_jugadores'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Eliminar el índice y la restricción única del email
    op.drop_index('ix_jugadores_email', table_name='jugadores')
    op.drop_constraint('jugadores_email_key', 'jugadores', type_='unique')
    
    # Eliminar la columna email
    op.drop_column('jugadores', 'email')

def downgrade() -> None:
    # Recrear la columna email
    op.add_column('jugadores', sa.Column('email', sa.String(), nullable=False))
    
    # Recrear el índice y la restricción única
    op.create_index('ix_jugadores_email', 'jugadores', ['email'], unique=True)
    op.create_unique_constraint('jugadores_email_key', 'jugadores', ['email']) 