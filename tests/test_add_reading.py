import datetime
import re

import bs4
import hyperlink

import helpers
from src.models import Reading


def test_add_reading_links_to_book(client, session, fake, logged_in_user):
    """
    When you add a reading, you should be redirected to a URL like /reading#book-1,
    so your browser jumps to the reading you just created.
    """
    resp = client.get("/reading")
    csrf_token = helpers.get_csrf_token(resp.data)

    book = helpers.create_book(session=session, fake=fake)
    note = fake.text()

    add_review_resp = client.post(
        "/add-reading",
        data={
            "csrf_token": csrf_token,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "identifiers": book.identifiers_json,
            "source_id": book.source_id,
            "image_url": book.image_url,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "note": note,
            "date_started": datetime.datetime.now().date().isoformat(),
        },
    )

    url = hyperlink.URL.from_text(add_review_resp.headers["Location"])

    assert url.path == ("reading",)

    fragment = url.fragment

    reading_id = re.match(r"^reading\-(?P<reading_id>\d+)$", fragment).group("reading_id")
    assert Reading.query.get(reading_id).note == note

    reading_page_resp = client.get("/reading")
    soup = bs4.BeautifulSoup(reading_page_resp.data, "html.parser")
    reading = soup.find("div", attrs={"id": fragment})

    assert reading is not None
    assert reading.find("h3", attrs={"class": "book-title"}).text.strip() == book.title


def test_malformed_add_reading_form_is_error(client, session, logged_in_user):
    resp = client.post("/add-reading", data={})
    assert resp.status_code == 400


def test_cannot_add_reading_if_not_logged_in(client, session):
    resp = client.post("/add-reading")
    assert resp.status_code == 401
