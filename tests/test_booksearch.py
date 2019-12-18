# -*- encoding: utf-8

import os

import betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
import pytest
import requests

from booksearch import lookup_google_books


def sanitize_google_books_api_key(interaction, current_cassette):
    req = interaction.data["request"]
    req["uri"] = req["uri"].replace(
        os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>"),
        "<API_KEY>"
    )

    resp = interaction.data["response"]
    resp["url"] = resp["url"].replace(
        os.environ.get("GOOGLE_BOOKS_API_KEY", "<API_KEY>"),
        "<API_KEY>"
    )


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


@pytest.mark.parametrize(
    "book_id, expected_identifiers",
    [
        # API returns both ISBN-10 and ISBN-13
        (
            "0K4RCTFXFTkC",
            [
                {"type": "ISBN_10", "identifier": "0618254358"},
                {"type": "ISBN_13", "identifier": "9780618254354"},
            ],
        ),
        # API includes the industryIdentifiers field, but not the ISBN-13.
        ("XaKdAQAACAAJ", [{"type": "OTHER", "identifier": "OCLC:939600576"}]),
    ],
)
def test_gets_identifiers_correctly(sess, api_key, book_id, expected_identifiers):
    result = lookup_google_books(sess=sess, api_key=api_key, search_query=book_id)

    book = next(r for r in result if r["id"] == book_id)
    assert book["identifiers"] == expected_identifiers


def test_handles_no_identifiers(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="PediaPress Foo Fighters"
    )

    book = next(r for r in result if r["id"] == "FI4eaajjC7sC")
    assert book["identifiers"] == []


@pytest.mark.parametrize(
    "book_id, expected_year",
    [
        # API returns '1990'
        ("aRYR1tnmKpEC", "1990"),
        # API returns '2014-03-01'
        ("tAMGoQEACAAJ", "2014"),
        # API returns '2003-04'
        ("sVbeAAAACAAJ", "2003"),
        # API returns no publishedDate field
        ("4B4eHLgO4iEC", ""),
    ],
)
def test_gets_year_correctly(sess, api_key, book_id, expected_year):
    result = lookup_google_books(sess=sess, api_key=api_key, search_query=book_id)

    book = next(r for r in result if r["id"] == book_id)
    assert book["year"] == expected_year
