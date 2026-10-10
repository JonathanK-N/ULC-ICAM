"""Create the isolated relational staging schema."""
from alembic import op
from migration_schema import metadata

revision = '0001_staging_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    metadata.create_all(op.get_bind())


def downgrade():
    metadata.drop_all(op.get_bind())
