# -*- encoding: utf-8

import pathlib
import random
import sys

from faker import Faker
from faker.providers import date_time, internet, misc
import pytest

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

from src import app, db as _db  # noqa
from src.models import Book, User  # noqa


@pytest.fixture(scope="session")
def fake():
    faker_inst = Faker()
    faker_inst.add_provider(date_time)
    faker_inst.add_provider(internet)
    faker_inst.add_provider(misc)
    return faker_inst


@pytest.fixture(scope="session")
def test_app(request):
    """Session-wide test `Flask` application."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def db(test_app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def user(session, fake):
    u = User(username=fake.name(), email_address=fake.email())
    session.add(u)
    return u


@pytest.fixture
def book(session, fake):
    bk = Book(
        title=fake.name(),
        author=", ".join(fake.name() for _ in range(random.randint(0, 5))),
        year=fake.numerify("####"),
        identifiers='[{"type": "ISBN_10", "value": "1234567890"}]',
        source_id=fake.numerify(),
    )
    session.add(bk)
    return bk
