"""empty message

Revision ID: 7b1e3826c969
Revises: ab2769f3ae7b
Create Date: 2023-03-08 19:46:33.613424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b1e3826c969'
down_revision = 'ab2769f3ae7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)

    # ### end Alembic commands ###
