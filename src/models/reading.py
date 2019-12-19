# -*- encoding: utf-8

from src import db
from .defaults import today
from .review import Review


class AlreadyReadingException(Exception):
    def __init__(self, book):
        self.book = book
        super().__init__(f"You are already reading {book.title}")


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_started = db.Column(db.Date, index=True, default=today)

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)

    # A book can only appear once in the list of books you're
    # currently reading
    __table_args__ = (db.UniqueConstraint("book_id", "user_id"),)

    @classmethod
    def create(cls, *, note, date_started, book, user):
        reading = Reading.query.filter_by(book=book, user=user).first()

        if reading is not None:
            raise AlreadyReadingException(book)
        else:
            new_reading = Reading(
                note=note, date_started=date_started, book=book, user=user
            )
            db.session.add(new_reading)
            db.session.commit()
            return new_reading

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
