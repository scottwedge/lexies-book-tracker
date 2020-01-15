import datetime

import bs4
import pytest


def test_no_heading_on_single_review(client, review):
    resp = client.get(f"/reviews/{review.id}")

    assert b"the 1 book i read at another time" not in resp.data


def test_no_spreadsheet_on_single_review(client, review):
    resp = client.get(f"/reviews/{review.id}")

    assert b"download as a spreadsheet" not in resp.data


def test_this_years_review_is_special(client, session, review):
    review.date_read = datetime.datetime.now().date()
    session.commit()

    resp = client.get("/read")
    expected_text = f"the 1 book i&rsquo;ve read so far in {review.date_read.year}"
    assert expected_text.encode("utf8") in resp.data


def test_no_leading_zero_on_dates(client, session, review):
    review.date_read = datetime.datetime(2019, 12, 1).date()
    session.commit()

    resp = client.get("/read")
    assert b"Read: 1 December 2019" in resp.data
    assert b"Read: 01 December 2019" not in resp.data


def test_no_add_review_form_if_not_logged_in(client, session, user):
    resp = client.get("/read")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    assert soup.find("div", attrs={"book-add-form"}) is None
