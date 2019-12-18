# -*- encoding: utf-8

import datetime

from src import db


def today():
    return datetime.datetime.now().date()


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
