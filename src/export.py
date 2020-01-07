import csv
import io

from .models import Review


def reviews_as_csv():
    buf = io.StringIO()

    writer = csv.DictWriter(
        buf,
        fieldnames=[
            "review_id",
            "title",
            "author",
            "year",
            "source_id",
            "image_url",
            "isbn_10",
            "isbn_13",
            "review_text",
            "date_read",
        ],
    )

    writer.writeheader()

    for review in Review.query.all():
        try:
            date_read = review.date_read.isoformat()
        except AttributeError:
            date_read = ""

        writer.writerow(
            {
                "review_id": review.id,
                "title": review.book.title,
                "author": review.book.author,
                "year": review.book.year,
                "source_id": review.book.source_id,
                "image_url": review.book.image_url or "",
                "isbn_10": review.book.isbn_10 or "",
                "isbn_13": review.book.isbn_13 or "",
                "review_text": review.review_text,
                "date_read": date_read,
            }
        )

    buf.seek(0)
    return io.BytesIO(buf.read().encode("utf-8"))
