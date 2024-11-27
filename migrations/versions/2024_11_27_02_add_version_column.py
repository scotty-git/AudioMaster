"""add version column

Revision ID: 2024_11_27_02
Revises: 
Create Date: 2024-11-27 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2024_11_27_02'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add version column to prompt_templates table if it doesn't exist
    op.add_column('prompt_templates', sa.Column('version', sa.Integer(), nullable=True))
    
    # Set default value for existing rows
    op.execute('UPDATE prompt_templates SET version = 1 WHERE version IS NULL')
    
    # Make version column not nullable after setting default values
    op.alter_column('prompt_templates', 'version',
                    existing_type=sa.Integer(),
                    nullable=False,
                    server_default='1')


def downgrade() -> None:
    op.drop_column('prompt_templates', 'version')
