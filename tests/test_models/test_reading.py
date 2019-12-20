# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import AlreadyReadingException, Reading, Review


def test_can_store_and_retrieve_currently_reading(session, fake, book, user):
    reading = Reading(note=fake.text(), book=book, user=user)
    session.add(reading)

    session.commit()

    assert Reading.query.get(reading.id) == reading


def test_same_user_cannot_be_reading_book_twice(session, fake, book, user):
    reading1 = Reading(note=fake.text(), book=book, user=user)
    reading2 = Reading(note=fake.text(), book=book, user=user)
    session.add(reading1)
    session.add(reading2)

    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint failed: reading.book_id, reading.user_id",
    ):
        session.commit()


def test_creates_new_reading(session, fake, book, user):
    reading = Reading.create(
        note=fake.text(), date_started=fake.date_object(), book=book, user=user
    )

    assert Reading.query.count() == 1
    assert Reading.query.get(reading.id) == reading


def test_does_not_create_duplicate_reading(session, fake, book, user):
    reading = Reading(note=fake.text(), book=book, user=user)
    session.add(reading)
    session.commit()

    with pytest.raises(
        AlreadyReadingException, match=f"You are already reading {book.title}"
    ):
        Reading.create(
            note=fake.text(), date_started=fake.date_object(), book=book, user=user
        )


def test_mark_as_read(session, fake, book, user):
    reading = Reading(note=fake.text(), book=book, user=user)
    session.add(reading)
    session.commit()

    assert Reading.query.count() == 1

    review_text = fake.text()
    date_read = fake.date_object()
    did_not_finish = fake.boolean()
    is_favourite = fake.boolean()

    review = reading.mark_as_read(
        review_text=review_text,
        date_read=date_read,
        did_not_finish=did_not_finish,
        is_favourite=is_favourite,
    )

    assert Reading.query.count() == 0
    assert Review.query.count() == 1

    assert Review.query.get(review.id) == review
    assert review.review_text == review_text
    assert review.date_read == date_read
    assert review.did_not_finish == did_not_finish
    assert review.is_favourite == is_favourite
    assert review.book == book
    assert review.user == user
