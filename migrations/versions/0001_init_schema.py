"""init schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE assetstatus AS ENUM ('UPLOADED', 'PROCESSING', 'READY', 'FAILED')")
    op.execute("CREATE TYPE interptype AS ENUM ('STEP', 'LINEAR')")

    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("music_object_key", sa.String(length=512), nullable=True),
        sa.Column("music_duration_sec", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("music_bpm", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create tracks table
    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create skeleton_sources table
    op.create_table(
        "skeleton_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("num_frames", sa.Integer(), nullable=True),
        sa.Column("num_joints", sa.Integer(), nullable=True),
        sa.Column("pose_model", sa.String(length=100), nullable=True),
        sa.Column("status", postgresql.ENUM("UPLOADED", "PROCESSING", "READY", "FAILED", name="assetstatus"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create skeleton_layers table
    op.create_table(
        "skeleton_layers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("skeleton_source_id", sa.Integer(), nullable=False),
        sa.Column("start_sec", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("end_sec", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skeleton_source_id"], ["skeleton_sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_skeleton_layers_track_start", "skeleton_layers", ["track_id", "start_sec"])
    op.create_index("idx_skeleton_layers_track_priority", "skeleton_layers", ["track_id", "priority"])

    # Create track_position_keyframes table
    op.create_table(
        "track_position_keyframes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("time_sec", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("x", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("y", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("interp", postgresql.ENUM("STEP", "LINEAR", name="interptype"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("track_id", "time_sec", name="uq_track_position_keyframes_track_time"),
    )
    op.create_index("idx_keyframes_track_time", "track_position_keyframes", ["track_id", "time_sec"])

    # Create videos table
    op.create_table(
        "videos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("duration_sec", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("status", postgresql.ENUM("UPLOADED", "PROCESSING", "READY", "FAILED", name="assetstatus"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("videos")
    op.drop_table("track_position_keyframes")
    op.drop_table("skeleton_layers")
    op.drop_table("skeleton_sources")
    op.drop_table("tracks")
    op.drop_table("projects")
    op.execute("DROP TYPE IF EXISTS interptype")
    op.execute("DROP TYPE IF EXISTS assetstatus")

