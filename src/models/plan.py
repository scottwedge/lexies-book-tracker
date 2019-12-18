# -*- encoding: utf-8

import datetime

from src import db


def today():
    return datetime.datetime.now().date()


class Plan(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
