"""Add friends and more info to user

Revision ID: a10a12ae6839
Revises: 36128b8403ca
Create Date: 2022-10-01 14:02:09.255213

"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = 'a10a12ae6839'
down_revision = '36128b8403ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_vision', schema=None) as batch_op:
        batch_op.add_column(sa.Column('friend_status', sa.Integer(), nullable=True))

        batch_op.create_index(batch_op.f('ix_user_vision_friend_status'), ['friend_status'], unique=False)

    op.execute("UPDATE user_vision SET friend_status = 1")
    with op.batch_alter_table('user_vision', schema=None) as batch_op:
        batch_op.alter_column('friend_status', existing_type=sa.INTEGER(), nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('invited_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('account_status', sa.Integer(), nullable=True))

        batch_op.alter_column('tg_alias',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.create_index(batch_op.f('ix_users_account_status'), ['account_status'], unique=False)

    op.execute("UPDATE users SET account_status = 1")
    op.execute("UPDATE users SET invited_by = 447411595")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('account_status', existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column('invited_by', existing_type=sa.INTEGER(), nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_account_status'))
        batch_op.alter_column('tg_alias',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('account_status')
        batch_op.drop_column('invited_by')

    with op.batch_alter_table('user_vision', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_vision_friend_status'))
        batch_op.drop_column('friend_status')

    # ### end Alembic commands ###
