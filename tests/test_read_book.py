"""
Tests for the "read book" page.
"""

import datetime as dt

import bs4

from src.models import Review


def test_can_add_book_without_read_date(client, logged_in_user, book, fake):
    resp = client.get("/read")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    csrf_token = soup.find("input", attrs={"id": "csrf_token"}).attrs["value"]

    resp = client.post(
        "/add-review",
        data={
            "csrf_token": csrf_token,
            "title": book.title,
            "author": book.author,
            "image_url": book.image_url,
            "source_id": book.source_id,
            "year": book.year,
            "identifiers": book.identifiers,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "review_text": fake.text(),
            "date_read": "",
        },
    )

    assert resp.status_code == 302

    resp = client.get("/read")
    assert b"I haven&rsquo;t read any books yet!" not in resp.data, resp.data

    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    title = soup.find("h3", attrs={"book-title"})
    assert book.title in title.text

    review = Review.query.get(1)
    assert review.date_read is None

    h3_text = {h3_tag.text.strip() for h3_tag in soup.find_all("h3")}
    assert "the 1 book i read at another time" in h3_text


def test_only_shows_another_time_list_if_nonempty(client, logged_in_user, book, fake):
    resp = client.get("/read")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    csrf_token = soup.find("input", attrs={"id": "csrf_token"}).attrs["value"]

    resp = client.post(
        "/add-review",
        data={
            "csrf_token": csrf_token,
            "title": book.title,
            "author": book.author,
            "image_url": book.image_url,
            "source_id": book.source_id,
            "year": book.year,
            "identifiers": book.identifiers,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "review_text": fake.text(),
            "date_read": dt.datetime.now().strftime("%Y-%m-%d"),
        },
    )

    assert resp.status_code == 302

    resp = client.get("/read")
    assert b"I haven&rsquo;t read any books yet!" not in resp.data, resp.data

    h3_text = {h3_tag.text.strip() for h3_tag in soup.find_all("h3")}
    assert "the 1 book i read at another time" not in h3_text
