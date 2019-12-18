# -*- encoding: utf-8

import re

import requests


def get_published_year(date_string):
    # The Google Books API returns the publishedDate field in a number of
    # forms, including 2010, 2009-08, 2019-04-15.
    m = re.match(r"^(?P<year>\d{4})(?:-\d{2}(?:-\d{2}))?$", date_string)

    try:
        return m.group("year")
    except AttributeError:
        pass


def get_isbn13(item):
    try:
        identifier = next(
            ind_id
            for ind_id in item["volumeInfo"].get("industryIdentifiers", [])
            if ind_id["type"] == "ISBN_13"
        )
    except StopIteration:
        return ""
    else:
        return identifier["identifier"]


def lookup_google_books(api_key, search_query):
    resp = requests.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": search_query, "key": api_key}
    )
    resp.raise_for_status()

    all_items = resp.json()["items"]

    return [
        {
            "id": item["id"],
            "title": item["volumeInfo"]["title"],
            "author": ", ".join(item["volumeInfo"]["authors"]),
            "isbn13": get_isbn13(item),
            "year": get_published_year(item["volumeInfo"].get("publishedDate", "")),
            "image_url": item["volumeInfo"].get("imageLinks", {}).get("thumbnail", ""),
        }
        for item in all_items
    ]
