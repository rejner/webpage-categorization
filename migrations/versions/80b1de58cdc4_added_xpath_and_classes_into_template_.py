"""Added xPath and Classes into Template Element

Revision ID: 80b1de58cdc4
Revises: 
Create Date: 2023-05-07 16:36:59.534046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80b1de58cdc4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('elements', sa.Column('xPath', sa.Text(), nullable=True))
    op.add_column('elements', sa.Column('classes', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('elements', 'classes')
    op.drop_column('elements', 'xPath')
    # ### end Alembic commands ###
