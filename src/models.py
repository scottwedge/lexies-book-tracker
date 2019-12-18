# -*- encoding: utf-8

import datetime
import json

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


def today():
    return datetime.datetime.now().date()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email_address = db.Column(db.String(256), unique=True)

    reviews = db.relationship("Review", backref="user", lazy="dynamic")
    currently_reading = db.relationship(
        "CurrentlyReading", backref="user", lazy="dynamic"
    )
    plans = db.relationship("Plan", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username!r}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    author = db.Column(db.String(500))
    year = db.Column(db.String(4))
    identifiers_json = db.Column(db.String(500))
    source_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    image_url = db.Column(db.String(500))

    reviews = db.relationship("Review", backref="book", lazy="dynamic")
    currently_reading = db.relationship(
        "CurrentlyReading", backref="book", lazy="dynamic"
    )
    plans = db.relationship("Plan", backref="book", lazy="dynamic")

    def identifiers(self):
        return json.loads(self.identifiers_json)

    @classmethod
    def create_or_get(cls, *, title, author, year, identifiers, source_id, image_url):
        """
        Get a book with these fields from the database -- creating one if
        it doesn't already exist.
        """
        book = Book.query.filter_by(source_id=source_id).first()

        if book is not None:
            return book
        else:
            new_book = Book(
                title=title,
                author=author,
                year=year,
                # The identifiers field is a JSON blob that I'm keeping around
                # because it might be useful for something later on.  It isn't
                # used anywhere yet, just kept as future-proofing -- if I want
                # to bring in more metadata later, this is a good way to get it.
                identifiers_json=json.dumps(identifiers),
                source_id=source_id,
                image_url=image_url,
            )
            db.session.add(new_book)
            db.session.commit()
            return new_book


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text)
    date_read = db.Column(db.Date, index=True, default=today)

    did_not_finish = db.Column(db.Boolean, default=False)
    is_favourite = db.Column(db.Boolean, default=False)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @classmethod
    def create(
        cls, *, review_text, date_read, did_not_finish, is_favourite, book, user
    ):
        review = Review(
            review_text=review_text,
            date_read=date_read,
            did_not_finish=did_not_finish,
            is_favourite=is_favourite,
            book=book,
            user=user,
        )

        db.session.add(review)
        db.session.commit()

        return review


class Plan(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_added = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class CurrentlyReading(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
