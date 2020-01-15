import datetime
import re

import bs4
import hyperlink

import helpers
from src.models import Review


def test_add_review_links_to_review(client, session, fake, review, logged_in_user):
    """
    When you add a review, you should be redirected to a URL like /review#book-1,
    so your browser jumps to the review you just created.
    """
    resp = client.get("/read")
    csrf_token = helpers.get_csrf_token(resp.data)

    book = helpers.create_book(session=session, fake=fake)
    review_text = fake.text()

    add_review_resp = client.post(
        "/add-review",
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
            "review_text": review_text,
            "date_read": datetime.datetime.now().date().isoformat(),
        },
    )

    url = hyperlink.URL.from_text(add_review_resp.headers["Location"])

    assert url.path == ("read",)

    fragment = url.fragment

    review_id = re.match(r"^book\-(?P<review_id>\d+)$", fragment).group("review_id")
    assert Review.query.get(review_id).review_text == review_text

    reading_page_resp = client.get("/read")
    soup = bs4.BeautifulSoup(reading_page_resp.data, "html.parser")
    review = soup.find("div", attrs={"id": fragment})

    assert review is not None
    assert review.find("h3", attrs={"class": "book-title"}).text.strip() == book.title


def test_malformed_add_review_form_is_error(client, session, logged_in_user):
    resp = client.post("/add-review", data={})
    assert resp.status_code == 400


def test_cannot_add_review_if_not_logged_in(client, session):
    resp = client.post("/add-review")
    assert resp.status_code == 401
