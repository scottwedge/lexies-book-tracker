# -*- encoding: utf-8

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Book, Plan, User


def test_can_store_and_retrieve_plan(session):
    book = Book(title="The Paper Menagerie", source_id="1234")
    user = User(username="ken")

    session.add(book)
    session.add(user)

    plan = Plan(
        note="I want to read this book",
        date_added=dt.datetime(2020, 1, 1).date(),
        book=book,
        user=user,
    )
    session.add(plan)

    session.commit()

    assert Plan.query.get(plan.id) == plan


def test_plan_default_date_added_is_today(session):
    book = Book(title="Programmed Inequality", source_id="1234")
    user = User(username="mar")

    session.add(book)
    session.add(user)

    plan = Plan(book=book, user=user)
    session.add(plan)

    session.commit()

    assert plan.date_added == dt.datetime.now().date()


def test_same_user_cannot_plan_to_read_book_twice(session):
    book = Book(title="Defying Hitler", source_id="1234")
    user = User(username="adolf")

    session.add(book)
    session.add(user)

    plan1 = Plan(book=book, user=user, note="I want to read this book")
    plan2 = Plan(book=book, user=user, note="I still want to read it")
    session.add(plan1)
    session.add(plan2)

    with pytest.raises(IntegrityError):
        session.commit()
