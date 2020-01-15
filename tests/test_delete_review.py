from src.models import Review


def test_can_delete_review(client, session, logged_in_user, review):
    resp = client.post(f"/delete-review/{review.id}")

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/read")

    assert Review.query.get(review.id) is None


def test_cannot_delete_non_existent_review(client, session, logged_in_user):
    resp = client.post(f"/delete-review/1")

    assert resp.status_code == 404


def test_cannot_delete_review_if_not_logged_in(client, session, review):
    client.post("/logout")
    resp = client.post(f"/delete-review/{review.id}")

    assert resp.status_code == 401
