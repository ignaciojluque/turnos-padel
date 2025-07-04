"""agrego campos emisor_nombre y emisor_cbu a Comprobante

Revision ID: d9d27417c3e8
Revises: bd782c08725e
Create Date: 2025-07-03 17:07:55.374442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9d27417c3e8'
down_revision = 'bd782c08725e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comprobante', schema=None) as batch_op:
        batch_op.add_column(sa.Column('emisor_nombre', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('emisor_cbu', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('emisor_cuit', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comprobante', schema=None) as batch_op:
        batch_op.drop_column('emisor_cuit')
        batch_op.drop_column('emisor_cbu')
        batch_op.drop_column('emisor_nombre')

    # ### end Alembic commands ###
