"""Create the isolated relational staging schema."""
from alembic import op
# Frozen revision: never import the evolving application schema.
from sqlalchemy import (MetaData, Table, Column, Integer, String, JSON, ForeignKey,
                        ForeignKeyConstraint)

metadata = MetaData()

roles = Table('roles', metadata, Column('name', String(20), primary_key=True))
users = Table('users', metadata,
              Column('username', String(80), primary_key=True),
              Column('role', String(20), ForeignKey('roles.name'), nullable=False),
              Column('password_hash', String(512), nullable=False),
              Column('payload', JSON, nullable=False))
courses = Table('courses', metadata, Column('id', Integer, primary_key=True),
                Column('payload', JSON, nullable=False))
teachers = Table('course_teachers', metadata,
                 Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
                 Column('username', String(80), ForeignKey('users.username'), primary_key=True))
enrollments = Table('enrollments', metadata,
                    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
                    Column('username', String(80), ForeignKey('users.username'), primary_key=True))
chapters = Table('chapters', metadata, Column('id', Integer, primary_key=True),
                 Column('course_id', Integer, ForeignKey('courses.id'), nullable=False),
                 Column('payload', JSON, nullable=False))
assignments = Table('assignments', metadata, Column('id', Integer, primary_key=True),
                    Column('course_id', Integer, ForeignKey('courses.id')),
                    Column('teacher', String(80), ForeignKey('users.username'), nullable=False),
                    Column('payload', JSON, nullable=False))
submissions = Table('submissions', metadata, Column('id', Integer, primary_key=True),
                    Column('assignment_id', Integer, ForeignKey('assignments.id'), nullable=False),
                    Column('student', String(80), ForeignKey('users.username'), nullable=False),
                    Column('payload', JSON, nullable=False))


def submission_record(name):
    return Table(name, metadata,
                 Column('submission_id', Integer, ForeignKey('submissions.id'), primary_key=True),
                 Column('payload', JSON, nullable=False))


grades = submission_record('grades')
plagiarism = submission_record('plagiarism')
groups = Table('assignment_groups', metadata,
               Column('assignment_id', Integer, ForeignKey('assignments.id'), primary_key=True),
               Column('group_id', String(80), primary_key=True),
               Column('payload', JSON, nullable=False))
group_members = Table('group_members', metadata,
                      Column('assignment_id', Integer, primary_key=True),
                      Column('group_id', String(80), primary_key=True),
                      Column('username', String(80), ForeignKey('users.username'), primary_key=True),
                      ForeignKeyConstraint(['assignment_id', 'group_id'],
                                           ['assignment_groups.assignment_id', 'assignment_groups.group_id']),
                      )
notifications = Table('notifications', metadata, Column('id', String(80), primary_key=True),
                       Column('username', String(80), ForeignKey('users.username')),
                       Column('payload', JSON, nullable=False))
audit_logs = Table('audit_logs', metadata, Column('id', String(80), primary_key=True),
                    Column('username', String(80), ForeignKey('users.username')),
                    Column('payload', JSON, nullable=False))
state = Table('application_state', metadata, Column('key', String(80), primary_key=True),
              Column('payload', JSON, nullable=False))
imports = Table('migration_imports', metadata,
                Column('source_sha256', String(64), primary_key=True),
                Column('counts', JSON, nullable=False))


revision = '0001_staging_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    metadata.create_all(op.get_bind())


def downgrade():
    metadata.drop_all(op.get_bind())
