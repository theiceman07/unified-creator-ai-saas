"""initial

Revision ID: 72c26537b6a1
Revises: 
Create Date: 2026-10-05 20:36:52.000000

"""
import os
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '72c26537b6a1'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Read the schema.sql file from the root directory
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'schema.sql')
    with open(schema_path, 'r') as f:
        sql = f.read()
    
    # Execute the raw SQL
    op.execute(sql)


def downgrade() -> None:
    pass
