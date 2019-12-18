# -*- encoding: utf-8

import json

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


def test_identifiers_are_json(session):
    identifiers = [{"type": "ISBN_10", "value": "1234567890"}]

    book = Book(identifiers_json=json.dumps(identifiers))

    assert book.identifiers() == identifiers


class TestCreateOrGet:
    def test_creates_new_book(self, session, fake):
        book = Book.create_or_get(
            title=fake.name(),
            author=fake.name(),
            year=fake.numerify("####"),
            identifiers=[{"type": "ISBN_10", "value": "1234567890"}],
            source_id=fake.numerify(),
            image_url=fake.uri(),
        )

        assert Book.query.count() == 1
        assert Book.query.get(book.id) == book

    def test_gets_existing_book(self, session, fake):
        title = fake.name()
        author = fake.name()
        year = fake.numerify("####")
        identifiers = [{"type": "ISBN_10", "value": "1234567890"}]
        source_id = fake.numerify()
        image_url = fake.uri()

        kwargs = {
            "title": title,
            "author": author,
            "year": year,
            "source_id": source_id,
            "image_url": image_url,
        }

        book = Book(identifiers_json=json.dumps(identifiers), **kwargs)
        session.add(book)
        session.commit()

        assert Book.create_or_get(identifiers=identifiers, **kwargs) == book
