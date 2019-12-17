# -*- encoding: utf-8

import datetime

from src import db


def today():
    return datetime.datetime.now().date()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    currently_reading = db.relationship("CurrentlyReading", backref="reader", lazy="dynamic")
    plans = db.relationship("Plan", backref="planner", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username!r}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn_13 = db.Column(db.String(13))
    title = db.Column(db.String(500))
    author = db.Column(db.String(500))
    source_id = db.Column(db.String(64))
    image_url = db.Column(db.String(500))
    source_blob = db.Column(db.Text)

    def __repr__(self):
        return f"<Book ISBN13={isbn_13!r}>"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text)
    date_read = db.Column(db.Date, index=True, default=today)

    did_not_finish = db.Column(db.Boolean, default=False)
    is_favourite = db.Column(db.Boolean, default=False)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    recommended_to_me = db.Column(db.Boolean, default=False)
    general_recommendation = db.Column(db.Boolean, default=False)
    looks_interesting = db.Column(db.Boolean, default=False)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class CurrentlyReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
