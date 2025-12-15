"""CORRECCIÓN: Añadir la columna faltante 'csv_filename' a fm_meta_data

Revision ID: 70a443bb0384
Revises: 006
Create Date: 2025-12-15 21:19:49.630131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'fm_meta_data', 
        sa.Column('csv_filename', sa.String(120), nullable=True)
    )


def downgrade():
    op.drop_column('fm_meta_data', 'csv_filename')
