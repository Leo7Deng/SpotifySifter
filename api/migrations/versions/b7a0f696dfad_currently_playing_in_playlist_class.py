"""currently_playing in playlist class

Revision ID: b7a0f696dfad
Revises: 
Create Date: 2023-10-11 00:11:15.857102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7a0f696dfad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currently_playing', sa.Boolean(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_currently_listening_playlist', type_='foreignkey')
        batch_op.drop_column('currently_listening')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currently_listening', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_user_currently_listening_playlist', 'playlist', ['currently_listening'], ['id'])

    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_column('currently_playing')

    # ### end Alembic commands ###
