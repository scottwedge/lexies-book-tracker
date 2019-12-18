# -*- encoding: utf-8

import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login


def today():
    return datetime.datetime.now().date()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email_address = db.Column(db.String(256))

    reviews = db.relationship("Review", backref="author", lazy="dynamic")
    currently_reading = db.relationship(
        "CurrentlyReading", backref="reader", lazy="dynamic"
    )
    plans = db.relationship("Plan", backref="planner", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username!r}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    author = db.Column(db.String(500))
    year = db.Column(db.String(4))
    identifers = db.Column(db.String(500))
    source_id = db.Column(db.String(64))
    image_url = db.Column(db.String(500))

    reviews = db.relationship("Review", backref="book", lazy="dynamic")
    currently_reading = db.relationship(
        "CurrentlyReading", backref="book", lazy="dynamic"
    )
    plans = db.relationship("Plan", backref="book", lazy="dynamic")

    def __repr__(self):
        return f"<Book {self.id}>"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text)
    date_read = db.Column(db.Date, index=True, default=today)

    did_not_finish = db.Column(db.Boolean, default=False)
    is_favourite = db.Column(db.Boolean, default=False)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class CurrentlyReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
