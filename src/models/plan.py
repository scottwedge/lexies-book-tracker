# -*- encoding: utf-8

from src import db
from .defaults import today
from .review import Review


class PlanAlreadyExistsException(Exception):
    def __init__(self, book):
        self.book = book
        super().__init__(f"You are already planning to read {book.title}")


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # A book can only appear once in your list of books you plan to read
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    @classmethod
    def create(cls, *, note, book, user):
        plan = Plan.query.filter_by(book=book, user=user).first()

        if plan is not None:
            raise PlanAlreadyExistsException(book)
        else:
            new_plan = Plan(note=note, book=book, user=user)
            db.session.add(new_plan)
            db.session.commit()
            return new_plan

    def mark_as_reviewed(self, *, review_text, date_read, did_not_finish, is_favourite):
        review = Review.create(
            review_text=review_text,
            date_read=date_read,
            did_not_finish=did_not_finish,
            is_favourite=is_favourite,
            book=self.book,
            user=self.user,
        )
        db.session.delete(self)
        db.session.commit()
        return review
