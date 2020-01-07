import csv
import datetime as dt
import io

from helpers import create_book
from src.models import Review


def test_can_export_reviews(client, session, fake, logged_in_user):
    book1 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )
    book2 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )

    review1 = Review(review_text=fake.text(), book=book1, user=logged_in_user)
    review2 = Review(review_text=fake.text(), book=book2, user=logged_in_user)

    session.add(review1)
    session.add(review2)
    session.commit()

    resp = client.get("/export/reviews")
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    assert csv_rows == [
        {
            "review_id": str(review1.id),
            "title": book1.title,
            "author": book1.author,
            "year": book1.year,
            "source_id": book1.source_id,
            "image_url": book1.image_url,
            "isbn_10": book1.isbn_10,
            "isbn_13": book1.isbn_13,
            "review_text": review1.review_text,
            "date_read": "",
        },
        {
            "review_id": str(review2.id),
            "title": book2.title,
            "author": book2.author,
            "year": book2.year,
            "source_id": book2.source_id,
            "image_url": book2.image_url,
            "isbn_10": book2.isbn_10,
            "isbn_13": book2.isbn_13,
            "review_text": review2.review_text,
            "date_read": "",
        },
    ]


def test_empty_isbn_is_empty_string_in_csv(client, session, fake, book, logged_in_user):
    book.isbn_10 = ""
    book.isbn_13 = ""
    review = Review(review_text=fake.text(), book=book, user=logged_in_user)

    session.add(review)
    session.commit()

    resp = client.get("/export/reviews")
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    row = csv_rows[0]
    assert row["isbn_10"] == ""
    assert row["isbn_13"] == ""


def test_review_date_is_isoformat(client, session, fake, book, logged_in_user):
    book.isbn_10 = ""
    book.isbn_13 = ""
    review = Review(
        review_text=fake.text(),
        date_read=dt.datetime.now().date(),
        book=book,
        user=logged_in_user,
    )

    session.add(review)
    session.commit()

    resp = client.get("/export/reviews")
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    row = csv_rows[0]
    assert row["date_read"] == dt.datetime.now().strftime("%Y-%m-%d")
