import random

from src.models import Book


def create_book(session, fake, isbn_10=None, isbn_13=None):
    isbn_10 = isbn_10 or ""
    isbn_13 = isbn_13 or ""

    bk = Book(
        title=fake.name(),
        author=", ".join(fake.name() for _ in range(random.randint(0, 5))),
        year=fake.numerify("####"),
        identifiers='[{"type": "ISBN_10", "value": "1234567890"}]',
        image_url=fake.uri(),
        source_id=fake.numerify(),
        isbn_10=isbn_10,
        isbn_13=isbn_13,
    )
    session.add(bk)
    return bk
