"""add columns field to fm_meta_data

Revision ID: 003
Revises: 002
Create Date: 2024-xx-xx

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ds_meta_data', 
                  sa.Column('extra_fields', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('ds_meta_data', 'extra_fields')