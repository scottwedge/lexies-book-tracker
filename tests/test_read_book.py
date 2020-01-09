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


def test_shows_books_in_review_order(client, session, fake, book, user):
    review1 = Review(
        review_text=fake.text(), date_read=dt.datetime(2001, 1, 1), book=book, user=user
    )
    review2 = Review(
        review_text=fake.text(), date_read=dt.datetime(2002, 1, 1), book=book, user=user
    )
    review3 = Review(review_text=fake.text(), date_read=None, book=book, user=user)

    session.add(review1)
    session.add(review2)
    session.add(review3)
    session.commit()

    resp = client.get("/read")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    h3_titles = [h3_tag.text.strip() for h3_tag in soup.find_all("h3")]

    assert (
        h3_titles.index("the 1 book i read in 2002")
        < h3_titles.index("the 1 book i read in 2001")
        < h3_titles.index("the 1 book i read at another time")
    )
