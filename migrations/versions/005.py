"""CORRECCIÓN: Forzar la actualización del ENUM 'publication_type' para incluir 'player'

Revision ID: ee1b5e08ace0
Revises: 004
Create Date: 2025-12-15 20:36:31.661803

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE ds_meta_data 
        MODIFY COLUMN publication_type 
        ENUM('none', 'player', 'season', 'playoffs', 'other') 
        NOT NULL;
        """
    )


def downgrade():
    pass
