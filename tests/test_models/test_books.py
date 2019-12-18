# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Book


def test_can_store_and_retrieve_book(session, fake):
    book = Book(title=fake.name(), source_id=fake.numerify())
    session.add(book)
    session.commit()

    assert Book.query.get(book.id) == book


def test_repr(session, fake):
    book = Book(title=fake.name(), source_id=fake.numerify())
    session.add(book)
    session.commit()

    assert repr(book) == "<Book 1>"


def test_source_id_must_be_unique(session, fake):
    source_id = fake.numerify()

    book1 = Book(title=fake.name(), source_id=source_id)
    session.add(book1)

    book2 = Book(title=fake.name(), source_id=source_id)
    session.add(book2)

    with pytest.raises(
        IntegrityError, match="UNIQUE constraint failed: book.source_id"
    ):
        session.commit()


def test_different_source_ids_are_allowed(session, fake):
    source_id = fake.numerify()

    book1 = Book(title=fake.name(), source_id=f"{source_id}_1")
    session.add(book1)

    book2 = Book(title=fake.name(), source_id=f"{source_id}_2")
    session.add(book2)

    session.commit()
    assert Book.query.count() == 2


def test_source_id_cannot_be_null(session, fake):
    book = Book(title=fake.name(), source_id=None)
    session.add(book)

    with pytest.raises(
        IntegrityError, match="NOT NULL constraint failed: book.source_id"
    ):
        session.commit()
