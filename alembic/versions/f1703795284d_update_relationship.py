"""update relationship

Revision ID: f1703795284d
Revises: 8e107ff51396
Create Date: 2025-03-15 12:35:17.271659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1703795284d'
down_revision: Union[str, None] = '8e107ff51396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoice', sa.Column('subscription_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'invoice', 'subscription', ['subscription_id'], ['id'])
    op.drop_column('invoice', 'paid_at')
    op.add_column('payment', sa.Column('subscription_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'payment', 'subscription', ['subscription_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_column('payment', 'subscription_id')
    op.add_column('invoice', sa.Column('paid_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'invoice', type_='foreignkey')
    op.drop_column('invoice', 'subscription_id')
    # ### end Alembic commands ###
