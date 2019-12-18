# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Book


def test_can_store_and_retrieve_book(session):
    bk = Book(title="We Go Forward")
    session.add(bk)
    session.commit()

    assert Book.query.filter_by(title="We Go Forward").first() == bk


def test_repr(session):
    bk = Book(title="To be Taught, If Fortunate")
    session.add(bk)
    session.commit()

    assert repr(bk) == "<Book 1>"


def test_source_id_must_be_unique(session):
    bk1 = Book(title="Going Postal", source_id="1234")
    session.add(bk1)

    bk2 = Book(title="All the Birds in the Sky", source_id="1234")
    session.add(bk2)

    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint failed: book.source_id"
    ):
        session.commit()
