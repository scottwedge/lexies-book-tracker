# -*- encoding: utf-8

import os
import pathlib
import secrets
import sys
import time

import betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from faker import Faker
from faker.providers import date_time, internet, misc
import pytest
import requests

import helpers

sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

from src import app, db as _db  # noqa
from src.models import Book, Reading, Review, User  # noqa


@pytest.fixture(scope="session")
def fake():
    faker_inst = Faker()
    faker_inst.add_provider(date_time)
    faker_inst.add_provider(internet)
    faker_inst.add_provider(misc)
    return faker_inst


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def client(test_app):
    with test_app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db(test_app, request):
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


@pytest.fixture(scope="function")
def user(session, fake):
    u = User(username=fake.name())
    session.add(u)
    return u


@pytest.fixture
def review(session, fake, book, user):
    review = Review(review_text=fake.text(), date_read=None, book=book, user=user)
    session.add(review)
    session.commit()

    return review


@pytest.fixture
def reading(session, fake, book, user):
    reading = Reading(note=fake.text(), date_started=None, book=book, user=user)
    session.add(reading)
    session.commit()

    return reading


@pytest.fixture(scope="function")
def logged_in_user(session, client, user):
    password = secrets.token_hex()
    user.set_password(password)
    session.commit()

    resp = client.get("/login")
    csrf_token = helpers.get_csrf_token(resp.data)

    client.post(
        "/login",
        data={
            "username": user.username,
            "password": password,
            "csrf_token": csrf_token,
        },
    )

    return user


@pytest.fixture(scope="function")
def book(session, fake):
    return helpers.create_book(session=session, fake=fake)


@pytest.fixture
def cassette_name(request):
    # This creates a cassette based on the pytest name.  Sometimes test
    # data contains URLs (e.g. parametrised tests), and the node.name
    # has slashes and colons (which are illegal in filesystems).
    #
    # Turn it into something usable.  It's very unlikely we'll have collisions,
    # and if we do they'll cause a failing test.
    return request.node.name.replace("/", "_").replace(":", "_")


def sanitize_google_books_api_key(interaction, _):  # pragma: no cover
    req = interaction.data["request"]
    req["uri"] = req["uri"].replace(
        os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>"), "<API_KEY>"
    )

    resp = interaction.data["response"]
    resp["url"] = resp["url"].replace(
        os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>"), "<API_KEY>"
    )


@pytest.fixture
def api_key(cassette_name):
    cassette = pathlib.Path("tests/cassettes") / f"{cassette_name}.json"

    # Betamax creates a cassette file as soon as it starts recording.
    # If the cassette was created recently, then assume this is a new test
    # and we want a fresh response with a real API key -- if not, use
    # the dummy API key saved in Betamax.
    try:
        is_cached = abs(time.time() - cassette.stat().st_mtime) > 10
    except FileNotFoundError:  # pragma: no cover
        is_cached = True

    if is_cached:
        return "<API_KEY>"
    else:  # pragma: no cover
        return os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>")


betamax.Betamax.register_serializer(PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = "tests/cassettes"
    config.before_record(callback=sanitize_google_books_api_key)

    config.default_cassette_options["serialize_with"] = PrettyJSONSerializer.name


@pytest.fixture
def sess(cassette_name):
    session = requests.Session()

    with betamax.Betamax(session).use_cassette(cassette_name):
        yield session
