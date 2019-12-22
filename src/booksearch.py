# -*- encoding: utf-8

import collections
import concurrent.futures
import html
import json
import re

import isbnlib
import requests
from smartypants import smartypants


def _apply_curly_quotes(s):
    return html.unescape(smartypants(s))


def _fix_encoding(s):
    # The data in the Google Books API sometimes returns mangled encodings, e.g.:
    # https://www.googleapis.com/books/v1/volumes?q=Present%20Laughter%20yU_hAuvMTQUC
    #
    # Decoding and fixing them properly is hard, but we can at least run some
    # substitutions over the string to catch common encoding bugs.

    # See http://www.i18nqa.com/debug/utf8-debug.html
    if b"\xC3" in s.encode("utf8"):
        for old, new in [
            ("\xC3\x80", "\xC0"),
            ("\xC3\x81", "\xC1"),
            ("\xC3\x82", "\xC2"),
            ("\xC3\x83", "\xC3"),
            ("\xC3\x84", "\xC4"),
            ("\xC3\x85", "\xC5"),
            ("\xC3\x86", "\xC6"),
            ("\xC3\x87", "\xC7"),
            ("\xC3\x88", "\xC8"),
            ("\xC3\x89", "\xC9"),
            ("\xC3\x8A", "\xCA"),
            ("\xC3\x8B", "\xCB"),
            ("\xC3\x8C", "\xCC"),
            ("\xC3\x8D", "\xCD"),
            ("\xC3\x8E", "\xCE"),
            ("\xC3\x8F", "\xCF"),
            ("\xC3\x90", "\xD0"),
            ("\xC3\x91", "\xD1"),
            ("\xC3\x92", "\xD2"),
            ("\xC3\x93", "\xD3"),
            ("\xC3\x94", "\xD4"),
            ("\xC3\x95", "\xD5"),
            ("\xC3\x96", "\xD6"),
            ("\xC3\x97", "\xD7"),
            ("\xC3\x98", "\xD8"),
            ("\xC3\x99", "\xD9"),
            ("\xC3\x9A", "\xDA"),
            ("\xC3\x9B", "\xDB"),
            ("\xC3\x9C", "\xDC"),
            ("\xC3\x9D", "\xDD"),
            ("\xC3\x9E", "\xDE"),
            ("\xC3\x9F", "\xDF"),
            ("\xC3\xA0", "\xE0"),
            ("\xC3\xA1", "\xE1"),
            ("\xC3\xA2", "\xE2"),
            ("\xC3\xA3", "\xE3"),
            ("\xC3\xA4", "\xE4"),
            ("\xC3\xA5", "\xE5"),
            ("\xC3\xA6", "\xE6"),
            ("\xC3\xA7", "\xE7"),
            ("\xC3\xA8", "\xE8"),
            ("\xC3\xA9", "\xE9"),
            ("\xC3\xAA", "\xEA"),
            ("\xC3\xAB", "\xEB"),
            ("\xC3\xAC", "\xEC"),
            ("\xC3\xAD", "\xED"),
            ("\xC3\xAE", "\xEE"),
            ("\xC3\xAF", "\xEF"),
            ("\xC3\xB0", "\xF0"),
            ("\xC3\xB1", "\xF1"),
            ("\xC3\xB2", "\xF2"),
            ("\xC3\xB3", "\xF3"),
            ("\xC3\xB4", "\xF4"),
            ("\xC3\xB5", "\xF5"),
            ("\xC3\xB6", "\xF6"),
            ("\xC3\xB7", "\xF7"),
            ("\xC3\xB8", "\xF8"),
            ("\xC3\xB9", "\xF9"),
            ("\xC3\xBA", "\xFA"),
            ("\xC3\xBB", "\xFB"),
            ("\xC3\xBC", "\xFC"),
            ("\xC3\xBD", "\xFD"),
            ("\xC3\xBE", "\xFE"),
            ("\xC3\xBF", "\xFF"),
        ]:
            s = s.replace(old, new)

    return s


def _get_authors(item):
    authors = item["volumeInfo"].get("authors", [])
    return ", ".join(_apply_curly_quotes(aut) for aut in authors)


def _get_identifiers(item):
    try:
        return item["volumeInfo"]["industryIdentifiers"]
    except KeyError:
        return []


def _get_identifier(item, ident_type):
    try:
        ident = next(
            ident
            for ident in item["volumeInfo"]["industryIdentifiers"]
            if ident["type"] == ident_type
        )
    except (StopIteration, KeyError):
        return ""
    else:
        return ident["identifier"]


def _get_published_year(item):
    try:
        published_date = item["volumeInfo"]["publishedDate"]
    except KeyError:
        return ""

    # The Google Books API returns the publishedDate field in a number of
    # forms, including 2010, 2009-08, 2019-04-15.
    m = re.match(r"^(?P<year>\d{4})(?:-\d{2})?(?:-\d{2})?$", published_date)

    try:
        return m.group("year")
    except AttributeError:  # pragma: no cover
        # In theory this error could be hit if the publishedDate doesn't
        # match this regex.  I've never seen it happen in practice, so
        # this is here defensively.
        # TODO: If you see a value that would cause this error to throw,
        # write a test for it and remove 'pragma: no cover'.
        return ""


def _get_image_url(sess, item):
    google_books_thumb = item["volumeInfo"].get("imageLinks", {}).get("thumbnail", "")

    # If there isn't a thumbnail in the Google Books API, we try the
    # Open Library API with the ISBN.  This can potentially be very slow,
    # if multiple books in a result don't have thumbnails.
    if google_books_thumb:
        return google_books_thumb
    else:
        identifiers = _get_identifiers(item)

        try:
            isbn = next(
                ident for ident in identifiers if ident["type"].startswith("ISBN_")
            )
        except StopIteration:
            return ""
        else:
            open_library_id = f"ISBN:{isbn['identifier']}"
            resp = sess.get(
                "https://openlibrary.org/api/books",
                params=[
                    ("bibkeys", open_library_id),
                    ("jscmd", "data"),
                    ("format", "json"),
                ],
            )
            try:
                return resp.json()[open_library_id]["cover"]["medium"]
            except (KeyError, ValueError):
                pass

    return ""


def lookup_google_books(*, sess=requests.Session(), api_key, search_query):
    resp = sess.get(
        "https://www.googleapis.com/books/v1/volumes",
        params=[("q", search_query), ("key", api_key), ("country", "UK")],
        headers={"User-Agent": "alexwlchan's book tracker"},
    )
    resp.raise_for_status()

    json_text = _fix_encoding(resp.text)
    try:
        all_items = json.loads(json_text)["items"]
    except KeyError:
        return []

    def _get_isbn(item, ident_type):
        value = _get_identifier(item, ident_type=ident_type)
        if value:
            return isbnlib.mask(value)
        else:
            return ""

    def _create_item(item):
        return {
            "id": item["id"],
            "title": _apply_curly_quotes(item["volumeInfo"]["title"]),
            "author": _get_authors(item),
            "identifiers": _get_identifiers(item),
            "year": _get_published_year(item),
            "image_url": _get_image_url(sess, item=item),
            "isbn13": _get_isbn(item, ident_type="ISBN_13"),
            "isbn10": _get_isbn(item, ident_type="ISBN_10"),
        }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # concurrent.futures.wait() may return the results in the wrong order
        # so hold their positions to rearrange them later.
        futures = collections.OrderedDict(
            [
                (executor.submit(_create_item, item), i)
                for i, item in enumerate(all_items)
            ]
        )

        completed_futures, _ = concurrent.futures.wait(futures)
        return [
            fut.result() for fut in sorted(completed_futures, key=lambda f: futures[f])
        ]
