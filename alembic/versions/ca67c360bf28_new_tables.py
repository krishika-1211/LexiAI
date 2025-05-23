"""new tables

Revision ID: ca67c360bf28
Revises: 31c705cbeba6
Create Date: 2025-03-12 15:56:48.165020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca67c360bf28'
down_revision: Union[str, None] = '31c705cbeba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invoice',
    sa.Column('invoice_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('amount_due', sa.Integer(), nullable=True),
    sa.Column('amount_paid', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('invoice_id')
    )
    op.create_table('payment',
    sa.Column('payment_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('currency', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('payment_id')
    )
    op.create_table('subscription',
    sa.Column('subscription_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('current_period_end', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('subscription_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscription')
    op.drop_table('payment')
    op.drop_table('invoice')
    # ### end Alembic commands ###
