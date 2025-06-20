"""Add user_id to Trade model

Revision ID: 669b0c637c13
Revises: 881e0039d8ed
Create Date: 2025-06-18 22:01:36.303956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '669b0c637c13'
down_revision = '881e0039d8ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trade', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trade', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
