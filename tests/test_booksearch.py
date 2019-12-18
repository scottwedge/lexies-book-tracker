# -*- encoding: utf-8

import os

import betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
import hyperlink
import pytest
import requests

from booksearch import lookup_google_books


def sanitize_google_books_api_key(interaction, current_cassette):
    req = interaction.data["request"]

    uri = hyperlink.URL.from_text(req["uri"])
    uri.set("key", "<API_KEY>")
    req["uri"] = str(uri)


@pytest.fixture
def api_key():
    return os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>")


betamax.Betamax.register_serializer(PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = "tests/cassettes"
    config.before_record(callback=sanitize_google_books_api_key)

    config.default_cassette_options["serialize_with"] = PrettyJSONSerializer.name


@pytest.fixture
def sess(request):
    session = requests.Session()

    with betamax.Betamax(session).use_cassette(request.node.name):
        yield session


def test_can_make_api_request(sess, api_key):
    lookup_google_books(sess=sess, api_key=api_key, search_query="fish")


def test_finds_isbn13(sess, api_key):
    result = lookup_google_books(sess=sess, api_key=api_key, search_query="fish")

    isbns = [book["isbn13"] for book in result]
    assert isbns == [
        "9781473574168",
        "9780747588696",
        "9781472139214",
        "9780907325895",
        "9781401394691",
        "9780412550300",
        "9780843142709",
        "9780141911274",
        "9780412408601",
        "9780763665784",
    ]


def test_copes_with_missing_authors(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="H-gTlLLybXAC"
    )

    assert len(result) == 1
    assert result[0]["author"] == ""


def test_combines_authors_into_string(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="2lBxWxua9H0C"
    )

    assert len(result) == 1
    assert result[0]["author"] == "Hugh Fearnley-Whittingstall, Nick Fisher"


def test_handles_encoding_correctly(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="yU_hAuvMTQUC"
    )

    assert set(r["author"] for r in result) == {"Noël Coward"}
