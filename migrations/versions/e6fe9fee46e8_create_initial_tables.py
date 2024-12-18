"""Create initial tables

Revision ID: e6fe9fee46e8
Revises: 
Create Date: 2024-11-26 14:18:49.176699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6fe9fee46e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('audiobooks', schema=None) as batch_op:
        batch_op.alter_column('outline_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)

    with op.batch_alter_table('book_outlines', schema=None) as batch_op:
        batch_op.alter_column('questionnaire_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)

    with op.batch_alter_table('questionnaire_responses', schema=None) as batch_op:
        batch_op.alter_column('template_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('questionnaire_responses', schema=None) as batch_op:
        batch_op.alter_column('template_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)

    with op.batch_alter_table('book_outlines', schema=None) as batch_op:
        batch_op.alter_column('questionnaire_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)

    with op.batch_alter_table('audiobooks', schema=None) as batch_op:
        batch_op.alter_column('outline_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)

    # ### end Alembic commands ###
