# -*- encoding: utf-8

import datetime as dt

from src.models import Review


def test_can_store_and_retrieve_review(session, book, user):
    review = Review(
        review_text="I enjoyed this book",
        date_read=dt.datetime(2019, 7, 1).date(),
        book=book,
        user=user,
    )
    session.add(review)

    session.commit()

    assert Review.query.get(review.id) == review


def test_review_defaults(session, book, user):
    review = Review(review_text="I enjoyed this book", book=book, user=user)
    session.add(review)

    session.commit()

    assert review.date_read == dt.datetime.now().date()
    assert not review.did_not_finish
    assert not review.is_favourite


def test_can_review_a_book_multiple_times(session, book, user):
    review1 = Review(book=book, user=user, review_text="I read this book")
    review2 = Review(book=book, user=user, review_text="I re-read this book")
    session.add(review1)
    session.add(review2)

    session.commit()
