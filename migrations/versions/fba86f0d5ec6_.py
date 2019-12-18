"""empty message

Revision ID: fba86f0d5ec6
Revises: 
Create Date: 2019-12-18 07:45:26.127150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fba86f0d5ec6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "book",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("author", sa.String(length=500), nullable=True),
        sa.Column("year", sa.String(length=4), nullable=True),
        sa.Column("isbn_13", sa.String(length=13), nullable=True),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("email_address", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.create_table(
        "currently_reading",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("book_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["book.id"],),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "plan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("date_added", sa.Date(), nullable=True),
        sa.Column("book_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["book.id"],),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plan_date_added"), "plan", ["date_added"], unique=False)
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("date_read", sa.Date(), nullable=True),
        sa.Column("did_not_finish", sa.Boolean(), nullable=True),
        sa.Column("is_favourite", sa.Boolean(), nullable=True),
        sa.Column("book_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["book.id"],),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_date_read"), "review", ["date_read"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_review_date_read"), table_name="review")
    op.drop_table("review")
    op.drop_index(op.f("ix_plan_date_added"), table_name="plan")
    op.drop_table("plan")
    op.drop_table("currently_reading")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")
    op.drop_table("book")
    # ### end Alembic commands ###
