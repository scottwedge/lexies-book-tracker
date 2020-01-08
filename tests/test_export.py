import csv
import datetime
import io

import bs4

from helpers import create_book
from src.models import Plan, Reading, Review


def today():
    return datetime.datetime.now().date()


def _find_download_link(client, path):
    resp = client.get(path)

    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    a_tags = soup.find_all("a")

    download_links = [a_t for a_t in a_tags if a_t.text == "download as a spreadsheet"]

    try:
        return download_links[0].attrs["href"]
    except IndexError:
        return


def test_can_export_reviews(client, session, fake, user):
    book1 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )
    book2 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )

    review1 = Review(review_text=fake.text(), book=book1, user=user)
    review2 = Review(review_text=fake.text(), book=book2, user=user)

    session.add(review1)
    session.add(review2)
    session.commit()

    download_link = _find_download_link(client, path="/read")
    assert download_link is not None

    resp = client.get(download_link)
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


def test_empty_isbn_is_empty_string_in_csv(client, session, fake, book, user):
    book.isbn_10 = ""
    book.isbn_13 = ""
    review = Review(review_text=fake.text(), book=book, user=user)

    session.add(review)
    session.commit()

    resp = client.get("/export/reviews")
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    row = csv_rows[0]
    assert row["isbn_10"] == ""
    assert row["isbn_13"] == ""


def test_review_date_is_isoformat(client, session, fake, book, user):
    book.isbn_10 = ""
    book.isbn_13 = ""
    review = Review(review_text=fake.text(), date_read=today(), book=book, user=user)

    session.add(review)
    session.commit()

    resp = client.get("/export/reviews")
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    row = csv_rows[0]
    assert row["date_read"] == today().strftime("%Y-%m-%d")


def test_can_export_plans(client, session, fake, user):
    book1 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )
    book2 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )

    plan1 = Plan(note=fake.text(), book=book1, user=user, date_added=today())
    plan2 = Plan(note=fake.text(), book=book2, user=user, date_added=today())

    session.add(plan1)
    session.add(plan2)
    session.commit()

    download_link = _find_download_link(client, path="/to-read")
    assert download_link is not None

    resp = client.get(download_link)
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    assert csv_rows == [
        {
            "plan_id": str(plan1.id),
            "title": book1.title,
            "author": book1.author,
            "year": book1.year,
            "source_id": book1.source_id,
            "image_url": book1.image_url,
            "isbn_10": book1.isbn_10,
            "isbn_13": book1.isbn_13,
            "note": plan1.note,
            "date_added": today().strftime("%Y-%m-%d"),
        },
        {
            "plan_id": str(plan2.id),
            "title": book2.title,
            "author": book2.author,
            "year": book2.year,
            "source_id": book2.source_id,
            "image_url": book2.image_url,
            "isbn_10": book2.isbn_10,
            "isbn_13": book2.isbn_13,
            "note": plan2.note,
            "date_added": today().strftime("%Y-%m-%d"),
        },
    ]


def test_can_export_reading(client, session, fake, logged_in_user):
    book1 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )
    book2 = create_book(
        session=session, fake=fake, isbn_10=fake.numerify(), isbn_13=fake.numerify()
    )

    reading1 = Reading(
        note=fake.text(), book=book1, user=logged_in_user, date_started=today()
    )
    reading2 = Reading(
        note=fake.text(), book=book2, user=logged_in_user, date_started=today()
    )

    session.add(reading1)
    session.add(reading2)
    session.commit()

    download_link = _find_download_link(client, path="/reading")
    assert download_link is not None

    resp = client.get(download_link)
    csv_buf = io.StringIO(resp.data.decode("utf-8"))

    csv_rows = [dict(row) for row in csv.DictReader(csv_buf)]

    assert csv_rows == [
        {
            "reading_id": str(reading1.id),
            "title": book1.title,
            "author": book1.author,
            "year": book1.year,
            "source_id": book1.source_id,
            "image_url": book1.image_url,
            "isbn_10": book1.isbn_10,
            "isbn_13": book1.isbn_13,
            "note": reading1.note,
            "date_started": today().strftime("%Y-%m-%d"),
        },
        {
            "reading_id": str(reading2.id),
            "title": book2.title,
            "author": book2.author,
            "year": book2.year,
            "source_id": book2.source_id,
            "image_url": book2.image_url,
            "isbn_10": book2.isbn_10,
            "isbn_13": book2.isbn_13,
            "note": reading2.note,
            "date_started": today().strftime("%Y-%m-%d"),
        },
    ]
