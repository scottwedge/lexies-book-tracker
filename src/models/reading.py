# -*- encoding: utf-8

from src import db


class Reading(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
