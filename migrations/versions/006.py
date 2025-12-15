"""CORRECCIÓN: Forzar la actualización del ENUM 'publication_type' para incluir 'PLAYER'





Revision ID: 221d6d25ee53


Revises: 005


Create Date: 2025-12-15 20:53:29.058410





"""


from alembic import op


import sqlalchemy as sa








# revision identifiers, used by Alembic.


revision = '006'


down_revision = '005'


branch_labels = None


depends_on = None








def upgrade():


    op.execute(


        """


        ALTER TABLE ds_meta_data 


        MODIFY COLUMN publication_type 


        ENUM('NONE', 'PLAYER', 'SEASON', 'PLAYOFFS', 'OTHER')


        NOT NULL;


        """


    )








def downgrade():


    pass