# -*- encoding: utf-8

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import Plan, PlanAlreadyExistsException


def test_can_store_and_retrieve_plan(session, fake, book, user):
    plan = Plan(note=fake.text(), date_added=fake.date_object(), book=book, user=user,)
    session.add(plan)

    session.commit()

    assert Plan.query.get(plan.id) == plan


def test_plan_default_date_added_is_today(session, book, user):
    plan = Plan(book=book, user=user)
    session.add(plan)

    session.commit()

    assert plan.date_added == dt.datetime.now().date()


def test_same_user_cannot_plan_to_read_book_twice(session, fake, book, user):
    plan1 = Plan(note=fake.text(), book=book, user=user)
    plan2 = Plan(note=fake.text(), book=book, user=user)
    session.add(plan1)
    session.add(plan2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_creates_new_plan(session, fake, book, user):
    plan = Plan.create(note=fake.text(), book=book, user=user)

    assert Plan.query.count() == 1
    assert Plan.query.get(plan.id) == plan


def test_does_not_create_duplicate_plan(session, fake, book, user):
    plan = Plan(note=fake.text(), book=book, user=user)
    session.add(plan)
    session.commit()

    with pytest.raises(
        PlanAlreadyExistsException,
        match=f"You are already planning to read {book.title}",
    ):
        Plan.create(note=fake.text(), book=book, user=user)
