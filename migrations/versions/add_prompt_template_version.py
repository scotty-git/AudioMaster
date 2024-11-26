"""add version tracking to prompt templates

Revision ID: add_prompt_template_version
Revises: previous_revision
Create Date: 2024-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'add_prompt_template_version'
down_revision = None  # Update this with your previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Add version column to prompt_templates
    op.add_column('prompt_templates', sa.Column('version', sa.Integer, server_default='1'))
    
    # Add last_edited_by column
    op.add_column('prompt_templates', sa.Column('last_edited_by', sa.String(36)))
    op.create_foreign_key(
        'fk_prompt_templates_last_edited_by_users',
        'prompt_templates', 'users',
        ['last_edited_by'], ['id']
    )
    
    # Add version history table
    op.create_table(
        'prompt_template_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('prompt_template_id', sa.String(36), nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('template_content', sa.Text, nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('edited_by', sa.String(36)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['prompt_template_id'], ['prompt_templates.id']),
        sa.ForeignKeyConstraint(['edited_by'], ['users.id'])
    )
    
    # Create index for faster version lookups
    op.create_index(
        'ix_prompt_template_versions_template_version',
        'prompt_template_versions',
        ['prompt_template_id', 'version'],
        unique=True
    )

def downgrade():
    # Remove version history table and its dependencies
    op.drop_index('ix_prompt_template_versions_template_version')
    op.drop_table('prompt_template_versions')
    
    # Remove foreign key and columns from prompt_templates
    op.drop_constraint('fk_prompt_templates_last_edited_by_users', 'prompt_templates')
    op.drop_column('prompt_templates', 'last_edited_by')
    op.drop_column('prompt_templates', 'version')
