# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Reading


def test_can_store_and_retrieve_currently_reading(session, book, user):
    reading = Reading(note="I am reading this book", book=book, user=user,)
    session.add(reading)

    session.commit()

    assert Reading.query.get(reading.id) == reading


def test_same_user_cannot_be_reading_book_twice(session, book, user):
    reading1 = Reading(book=book, user=user, note="I am reading this book")
    reading2 = Reading(book=book, user=user, note="I am still reading it")
    session.add(reading1)
    session.add(reading2)

    with pytest.raises(IntegrityError):
        session.commit()
