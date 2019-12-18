# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import AlreadyReadingException, Reading


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
        match="UNIQUE constraint failed: reading.book_id, reading.user_id"
    ):
        session.commit()


def test_creates_new_reading(session, fake, book, user):
    reading = Reading.create(note=fake.text(), book=book, user=user)

    assert Reading.query.count() == 1
    assert Reading.query.get(reading.id) == reading


def test_does_not_create_duplicate_reading(session, fake, book, user):
    reading = Reading(note=fake.text(), book=book, user=user)
    session.add(reading)
    session.commit()

    with pytest.raises(
        AlreadyReadingException,
        match=f"You are already reading {book.title}"
    ):
        Reading.create(note=fake.text(), book=book, user=user)
