import random

import bs4

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


def get_csrf_token(client, *, path):
    resp = client.get(path)
    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    return soup.find("input", attrs={"id": "csrf_token"}).attrs["value"]


def is_redirect(resp, *, location):
    return resp.status_code == 302 and resp.headers["Location"].endswith(location)


def is_flashed(resp, *, expected_message):
    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    messages = soup.find("div", attrs={"id": "messages"})
    message_text = [div.text.strip() for div in messages.find_all("div")]
    return expected_message in message_text
