import datetime

import pytest

from src.models import Review


@pytest.fixture
def review(session, fake, book, user):
    review = Review(review_text=fake.text(), date_read=None, book=book, user=user)
    session.add(review)
    session.commit()

    return review


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
