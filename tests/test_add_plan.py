import datetime
import re

import bs4
import hyperlink

import helpers
from src.models import Plan


def test_add_plan_links_to_book(client, session, fake, logged_in_user):
    """
    When you add a plan, you should be redirected to a URL like /to-read#plan-1,
    so your browser jumps to the reading you just created.
    """
    resp = client.get("/to-read")
    csrf_token = helpers.get_csrf_token(resp.data)

    book = helpers.create_book(session=session, fake=fake)
    note = fake.text()

    add_review_resp = client.post(
        "/add-plan",
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
            "date_added": datetime.datetime.now().date().isoformat(),
        },
    )

    url = hyperlink.URL.from_text(add_review_resp.headers["Location"])

    assert url.path == ("to-read",)

    fragment = url.fragment

    plan_id = re.match(r"^plan\-(?P<plan_id>\d+)$", fragment).group("plan_id")
    assert Plan.query.get(plan_id).note == note

    plan_page_resp = client.get("/to-read")
    soup = bs4.BeautifulSoup(plan_page_resp.data, "html.parser")
    plan = soup.find("div", attrs={"id": fragment})

    assert plan is not None
    assert plan.find("h3", attrs={"class": "book-title"}).text.strip() == book.title


def test_malformed_add_plan_form_is_error(client, session, logged_in_user):
    resp = client.post("/add-plan", data={})
    assert resp.status_code == 400


def test_cannot_add_plan_if_not_logged_in(client, session):
    resp = client.post("/add-plan")
    assert resp.status_code == 401
