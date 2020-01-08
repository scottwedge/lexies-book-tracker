# -*- encoding: utf-8

import json

from src import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    author = db.Column(db.String(500))
    year = db.Column(db.String(4))
    identifiers_json = db.Column(db.String(500))
    source_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    image_url = db.Column(db.String(500))

    isbn_10 = db.Column(db.String(25))
    isbn_13 = db.Column(db.String(25))

    reviews = db.relationship("Review", backref="book", lazy="dynamic")
    reading = db.relationship("Reading", backref="book", lazy="dynamic")
    plans = db.relationship("Plan", backref="book", lazy="dynamic")

    def identifiers(self):
        return json.loads(self.identifiers_json)

    @classmethod
    def create_or_get(
        cls, *, title, author, year, identifiers, isbn_10, isbn_13, source_id, image_url
    ):
        """
        Get a book with these fields from the database -- creating one if
        it doesn't already exist.
        """
        book = Book.query.filter_by(source_id=source_id).first()

        if not isinstance(identifiers, str):
            identifiers_json = json.dumps(identifiers)
        else:
            identifiers_json = identifiers

        if book is not None:
            return book
        else:
            print(identifiers)
            new_book = Book(
                title=title,
                author=author,
                year=year,
                # The identifiers field is a JSON blob that I'm keeping around
                # because it might be useful for something later on.  It isn't
                # used anywhere yet, just kept as future-proofing -- if I want
                # to bring in more metadata later, this is a good way to get it.
                identifiers_json=identifiers_json,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                source_id=source_id,
                image_url=image_url,
            )
            db.session.add(new_book)
            db.session.commit()
            return new_book
