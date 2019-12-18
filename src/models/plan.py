# -*- encoding: utf-8

import datetime

from src import db


def today():
    return datetime.datetime.now().date()


class PlanAlreadyExistsException(Exception):
    def __init__(self, book):
        self.book = book
        super().__init__(f"You are already planning to read {book.title}")


class Plan(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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
