"""Delete playlist in database

Revision ID: ca778430db1b
Revises: f673911a010c
Create Date: 2023-10-13 15:18:24.733821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca778430db1b'
down_revision = 'f673911a010c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('delete_playlist', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_column('delete_playlist')

    # ### end Alembic commands ###
