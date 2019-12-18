# -*- encoding: utf-8

import datetime as dt

from src.models import Book, Review, User


def test_can_store_and_retrieve_review(session):
    book = Book(title="Exhalation", source_id="1234")
    user = User(username="ted")

    session.add(book)
    session.add(user)

    review = Review(
        review_text="I enjoyed this book",
        date_read=dt.datetime(2019, 7, 1).date(),
        book_id=book.id,
        user_id=user.id
    )
    session.add(review)

    session.commit()

    retrieved_review = Review.query.get(review.id)
    assert retrieved_review == review


def test_review_defaults(session):
    book = Book(title="White Fragility", source_id="1234")
    user = User(username="vlad")

    session.add(book)
    session.add(user)

    review = Review(
        review_text="I enjoyed this book", book_id=book.id, user_id=user.id
    )
    session.add(review)

    session.commit()

    assert review.date_read == dt.datetime.now().date()
    assert not review.did_not_finish
    assert not review.is_favourite


def test_can_review_a_book_multiple_times(session):
    book = Book(title="IBM and the Holocaust", source_id="1234")
    user = User(username="edwin")

    session.add(book)
    session.add(user)

    review1 = Review(
        review_text="I read this book", book_id=book.id, user_id=user.id
    )
    review2 = Review(
        review_text="I re-read this book", book_id=book.id, user_id=user.id
    )
    session.add(review1)
    session.add(review2)

    session.commit()
