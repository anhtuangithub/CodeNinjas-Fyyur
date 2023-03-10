"""empty message

Revision ID: ab2769f3ae7b
Revises: 9752fd1e3a85
Create Date: 2023-03-05 22:02:58.267160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab2769f3ae7b'
down_revision = '9752fd1e3a85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
