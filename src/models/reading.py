# -*- encoding: utf-8

from src import db


class AlreadyReadingException(Exception):
    def __init__(self, book):
        self.book = book
        super().__init__(f"You are already reading {book.title}")


class Reading(db.Model):
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)

    @classmethod
    def create(cls, *, note, book, user):
        reading = Reading.query.filter_by(book=book, user=user).first()

        if reading is not None:
            raise AlreadyReadingException(book)
        else:
            new_reading = Reading(note=note, book=book, user=user)
            db.session.add(new_reading)
            db.session.commit()
            return new_reading
