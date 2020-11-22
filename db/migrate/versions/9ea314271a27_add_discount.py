"""Add discount

Revision ID: 9ea314271a27
Revises: 261a0dd175e8
Create Date: 2020-11-22 17:15:15.206384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ea314271a27'
down_revision = '261a0dd175e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credits', sa.Column('discount', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('credits', 'discount')
    # ### end Alembic commands ###
