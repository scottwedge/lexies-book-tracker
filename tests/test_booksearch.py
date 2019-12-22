# -*- encoding: utf-8

import os
import pathlib
import time

import betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
import pytest
import requests

from booksearch import lookup_google_books


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
def cassette_name(request):
    # This creates a cassette based on the pytest name.  Sometimes test
    # data contains URLs (e.g. parametrised tests), and the node.name
    # has slashes and colons (which are illegal in filesystems).
    #
    # Turn it into something usable.  It's very unlikely we'll have collisions,
    # and if we do they'll cause a failing test.
    return request.node.name.replace("/", "_").replace(":", "_")


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
    else:
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

    book = [r for r in result if r["id"] == book_id].pop()
    assert book["identifiers"] == expected_identifiers


def test_handles_no_identifiers(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="PediaPress Foo Fighters"
    )

    book = [r for r in result if r["id"] == "FI4eaajjC7sC"].pop()
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

    book = [r for r in result if r["id"] == book_id].pop()
    assert book["year"] == expected_year


@pytest.mark.parametrize(
    "book_id, expected_image_url",
    [
        # API doesn't have an "imageLinks" block
        ("chcnvwEACAAJ", ""),
        # API has an "imageLinks" dict and a "thumbnail" field
        (
            "DJN_72oR4gkC",
            "http://books.google.com/books/content?id=DJN_72oR4gkC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        ),
    ],
)
def test_gets_image_url_correctly(sess, api_key, book_id, expected_image_url):
    result = lookup_google_books(sess=sess, api_key=api_key, search_query=book_id)

    book = [r for r in result if r["id"] == book_id].pop()
    assert book["image_url"] == expected_image_url


def test_search_with_no_results_is_empty(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="F4744518-1E7B-44F8-9AA1-D837FCD2E679"
    )

    assert result == []


def test_renders_curly_quote_in_results(sess, api_key):
    result = lookup_google_books(
        sess=sess, api_key=api_key, search_query="9780571311873"
    )

    book = [r for r in result if r["isbn13"] == "978-0-571-31187-3"].pop()

    assert book["title"] == "Old Possum’s Book of Practical Cats"
