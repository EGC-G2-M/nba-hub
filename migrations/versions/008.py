"""CORRECCIÓN: Hacer 'uvl_filename' nullable en fm_meta_data

Revision ID: 6a4ac5ef9823
Revises: 007
Create Date: 2025-12-15 21:36:21.980593

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # 1. ELIMINAR la columna 'uvl_filename' (Si existe en la base de datos remota)
    # Hacemos esto primero para resolver el error de NOT NULL
    try:
        op.drop_column('fm_meta_data', 'uvl_filename')
    except Exception:
        pass


def downgrade():
    # Define la lógica inversa aquí si es necesario.
    # Por ejemplo, añadir de nuevo 'uvl_filename' y hacer nullable 'csv_filename'.
    pass
