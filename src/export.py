import csv
import io

from .models import Plan, Reading, Review


def _book_as_csv_row(book):
    return {
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "source_id": book.source_id,
        "image_url": book.image_url or "",
        "isbn_10": book.isbn_10 or "",
        "isbn_13": book.isbn_13 or "",
    }


def _create_stringio_csv(fieldnames, rows):
    buf = io.StringIO()

    writer = csv.DictWriter(buf, fieldnames=fieldnames)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    buf.seek(0)
    return io.BytesIO(buf.read().encode("utf-8"))


BOOK_CSV_FIELDS = [
    "title",
    "author",
    "year",
    "source_id",
    "image_url",
    "isbn_10",
    "isbn_13",
]


def reviews_as_csv():
    fieldnames = ["review_id"] + BOOK_CSV_FIELDS + ["review_text", "date_read"]

    def _rows():
        for review in Review.query.all():
            try:
                date_read = review.date_read.isoformat()
            except AttributeError:
                date_read = ""

            row = _book_as_csv_row(review.book)
            row.update(
                {
                    "review_id": review.id,
                    "review_text": review.review_text,
                    "date_read": date_read,
                }
            )

            yield row

    return _create_stringio_csv(fieldnames=fieldnames, rows=_rows())


def _format_date(d):
    try:
        return d.isoformat()
    except AttributeError:
        assert d is None, d
        return ""


def reading_as_csv():
    fieldnames = ["reading_id"] + BOOK_CSV_FIELDS + ["note", "date_started"]

    def _rows():
        for reading in Reading.query.all():
            row = _book_as_csv_row(reading.book)
            row.update(
                {
                    "reading_id": reading.id,
                    "note": reading.note,
                    "date_started": _format_date(reading.date_started),
                }
            )

            yield row

    return _create_stringio_csv(fieldnames=fieldnames, rows=_rows())


def plans_as_csv():
    fieldnames = ["plan_id"] + BOOK_CSV_FIELDS + ["note", "date_added"]

    def _rows():
        for plan in Plan.query.all():
            row = _book_as_csv_row(plan.book)
            row.update(
                {
                    "plan_id": plan.id,
                    "note": plan.note,
                    "date_added": _format_date(plan.date_added),
                }
            )

            yield row

    return _create_stringio_csv(fieldnames=fieldnames, rows=_rows())
