# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import CurrentlyReading


def test_can_store_and_retrieve_currently_reading(session, book, user):
    reading = CurrentlyReading(note="I am reading this book", book=book, user=user,)
    session.add(reading)

    session.commit()

    assert CurrentlyReading.query.get(reading.id) == reading


def test_same_user_cannot_be_reading_book_twice(session, book, user):
    reading1 = CurrentlyReading(book=book, user=user, note="I am reading this book")
    reading2 = CurrentlyReading(book=book, user=user, note="I am still reading it")
    session.add(reading1)
    session.add(reading2)

    with pytest.raises(IntegrityError):
        session.commit()
