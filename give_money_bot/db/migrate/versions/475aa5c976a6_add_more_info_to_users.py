"""Add more info to users

Revision ID: 475aa5c976a6
Revises: e5a51715598b
Create Date: 2022-05-18 00:22:41.246473

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '475aa5c976a6'
down_revision = 'e5a51715598b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('note', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('tg_alias', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('tg_name', sa.String(), nullable=True))
    op.execute(
        """
        UPDATE users SET phone_number = '', note = '', tg_alias = '', tg_name = ''
    """
    )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('phone_number', nullable=False)
        batch_op.alter_column('note', nullable=False)
        batch_op.alter_column('tg_alias', nullable=False)
        batch_op.alter_column('tg_name', nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('tg_name')
        batch_op.drop_column('tg_alias')
        batch_op.drop_column('note')
        batch_op.drop_column('phone_number')

    # ### end Alembic commands ###
