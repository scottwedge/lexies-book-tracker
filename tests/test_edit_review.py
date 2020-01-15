import datetime

import helpers
from src.models import Review


def test_can_edit_review(client, session, logged_in_user, review, fake):
    new_review_text = fake.text()
    new_date_read = datetime.datetime.now().date()
    new_did_not_finish = not review.did_not_finish
    new_is_favourite = not review.is_favourite

    assert new_review_text != review.review_text
    assert new_date_read != review.date_read

    resp = client.get(f"/reviews/{review.id}")
    csrf_token = helpers.get_csrf_token(resp.data)

    edit_review_resp = client.post("/edit-review", data={
        "csrf_token": csrf_token,
        "review_text": new_review_text,
        "review_id": review.id,
        "date_read": new_date_read.isoformat(),
        "did_not_finish": new_did_not_finish,
        "is_favourite": new_is_favourite,
    })

    assert edit_review_resp.status_code == 302
    assert edit_review_resp.headers["Location"].endswith(f"/reviews/{review.id}")

    stored_review = Review.query.get(review.id)
    assert stored_review.review_text == new_review_text
    assert stored_review.date_read == new_date_read
    assert stored_review.did_not_finish == new_did_not_finish
    assert stored_review.is_favourite == new_is_favourite


def test_malformed_edit_review_form_is_error(client, session, logged_in_user):
    resp = client.post("/edit-review", data={})
    assert resp.status_code == 400


def test_cannot_edit_review_if_not_logged_in(client, session):
    resp = client.post("/edit-review")
    assert resp.status_code == 401
