"""update jugadores table

Revision ID: 001_update_jugadores
Revises: 
Create Date: 2024-01-24 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_update_jugadores'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Eliminar las restricciones de clave foránea
    op.drop_constraint('parejas_partida_jugador1_id_fkey', 'parejas_partida', type_='foreignkey')
    op.drop_constraint('parejas_partida_jugador2_id_fkey', 'parejas_partida', type_='foreignkey')
    op.drop_constraint('resultados_jugador_id_fkey', 'resultados', type_='foreignkey')
    
    # Eliminar la tabla jugadores existente
    op.drop_table('jugadores')
    
    # Crear la nueva tabla jugadores
    op.create_table(
        'jugadores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('apellidos', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('telefono', sa.String(), nullable=False),
        sa.Column('club', sa.String(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('campeonato_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campeonato_id'], ['campeonatos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('nombre', 'apellidos', name='uix_nombre_apellidos')
    )
    op.create_index(op.f('ix_jugadores_id'), 'jugadores', ['id'], unique=False)
    op.create_index(op.f('ix_jugadores_nombre'), 'jugadores', ['nombre'], unique=False)
    op.create_index(op.f('ix_jugadores_apellidos'), 'jugadores', ['apellidos'], unique=False)
    op.create_index(op.f('ix_jugadores_email'), 'jugadores', ['email'], unique=True)
    
    # Recrear las restricciones de clave foránea
    op.create_foreign_key('parejas_partida_jugador1_id_fkey', 'parejas_partida', 'jugadores', ['jugador1_id'], ['id'])
    op.create_foreign_key('parejas_partida_jugador2_id_fkey', 'parejas_partida', 'jugadores', ['jugador2_id'], ['id'])
    op.create_foreign_key('resultados_jugador_id_fkey', 'resultados', 'jugadores', ['jugador_id'], ['id'])

def downgrade() -> None:
    # Eliminar las restricciones de clave foránea
    op.drop_constraint('parejas_partida_jugador1_id_fkey', 'parejas_partida', type_='foreignkey')
    op.drop_constraint('parejas_partida_jugador2_id_fkey', 'parejas_partida', type_='foreignkey')
    op.drop_constraint('resultados_jugador_id_fkey', 'resultados', type_='foreignkey')
    
    # Eliminar los índices
    op.drop_index(op.f('ix_jugadores_email'), table_name='jugadores')
    op.drop_index(op.f('ix_jugadores_apellidos'), table_name='jugadores')
    op.drop_index(op.f('ix_jugadores_nombre'), table_name='jugadores')
    op.drop_index(op.f('ix_jugadores_id'), table_name='jugadores')
    
    # Eliminar la tabla
    op.drop_table('jugadores') 