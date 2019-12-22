# -*- encoding: utf-8

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import User


def test_can_store_and_retrieve_user(session):
    u = User(username="alexwlchan", password_hash="123")
    session.add(u)
    session.commit()

    assert User.query.filter_by(username="alexwlchan").first() == u


def test_user_repr():
    u = User(username="example")
    assert repr(u) == "<User 'example'>"


def test_can_set_user_password(session):
    u = User(username="example")
    session.add(u)
    session.commit()

    password = "passw0rd!"
    u.set_password(password)
    session.commit()

    u = User.query.filter_by(username="example").first()
    assert u.check_password(password)
    assert not u.check_password("wrong_password")

    new_password = "correct-horse-battery-staple"
    u.set_password(new_password)
    session.commit()

    u = User.query.filter_by(username="example").first()
    assert u.check_password(new_password)
    assert not u.check_password(password)


def test_requires_username(session):
    u = User(username=None)
    session.add(u)

    with pytest.raises(
        IntegrityError, match="NOT NULL constraint failed: user.username"
    ):
        session.commit()


def test_usernames_must_be_unique(session):
    u1 = User(username="example")
    session.add(u1)

    u2 = User(username="example")
    session.add(u2)

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed: user.username"):
        session.commit()


def test_different_usernames_are_allowed(session):
    u1 = User(username="alice")
    session.add(u1)

    u2 = User(username="bob")
    session.add(u2)

    session.commit()
    assert User.query.count() == 2
