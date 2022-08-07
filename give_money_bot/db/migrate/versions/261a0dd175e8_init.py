"""Init

Revision ID: 261a0dd175e8
Revises: 
Create Date: 2020-11-22 14:53:27.291955

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "261a0dd175e8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credits',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('to_id', sa.Integer(), nullable=False),
    sa.Column('from_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('text_info', sa.String(), nullable=False),
    sa.Column('returned', sa.Boolean(), nullable=False),
    sa.Column('return_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('credits')
    # ### end Alembic commands ###

