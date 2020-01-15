import bs4
import pytest

import helpers
from src.models import Plan, Reading, Review


@pytest.mark.parametrize(
    "path",
    [
        "/add-plan",
        "/add-reading",
        "/add-review",
        "/delete-plan/1",
        "/delete-reading/1",
        "/delete-review/1",
        "/edit-plan/1",
        "/edit-reading/1",
        "/edit-review",
        "/mark_as_read/1",
        "/mark_plan_as_read/1",
        "/move_plan_to_reading/1",
    ],
)
def test_cannot_post_to_route_if_not_logged_in(client, session, user, path):
    resp = client.post(path)
    assert resp.status_code == 401


@pytest.mark.parametrize(
    "path", ["/add-plan", "/add-reading", "/add-review", "/edit-review"],
)
def test_invalid_form_data_is_error(client, session, logged_in_user, path):
    resp = client.post(path, data={})
    assert resp.status_code == 400


def test_cannot_edit_review_with_invalid_form_data(
    client, session, logged_in_user, review
):
    resp = client.post("/edit-review", data={})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "path", ["/edit-plan/{plan_id}", "/mark_plan_as_read/{plan_id}"]
)
def test_cannot_edit_plan_with_invalid_form_data(
    client, session, logged_in_user, plan, path
):
    path = path.format(plan_id=plan.id)
    resp = client.post(path, data={})
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "path", ["/edit-reading/{reading_id}", "/mark_as_read/{reading_id}"]
)
def test_cannot_edit_reading_with_invalid_form_data(
    client, session, logged_in_user, reading, path
):
    path = path.format(reading_id=reading.id)
    resp = client.post(path, data={})
    assert resp.status_code == 400


class TestEditRoutes:
    def test_can_edit_review(self, client, session, logged_in_user, review, fake):
        new_review_text = fake.text()
        new_date_read = fake.date_object()
        new_did_not_finish = not review.did_not_finish
        new_is_favourite = not review.is_favourite

        assert review.review_text != new_review_text
        assert review.date_read != new_date_read
        assert review.did_not_finish != new_did_not_finish
        assert review.is_favourite != new_is_favourite

        csrf_token = helpers.get_csrf_token(client, path=f"/reviews/{review.id}")

        resp = client.post(
            "/edit-review",
            data={
                "csrf_token": csrf_token,
                "review_id": review.id,
                "review_text": new_review_text,
                "date_read": new_date_read.isoformat(),
                "did_not_finish": new_did_not_finish,
                "is_favourite": new_is_favourite,
            },
        )

        assert helpers.is_redirect(resp, location=f"/reviews/{review.id}")

        stored_review = Review.query.get(review.id)

        assert stored_review.review_text == new_review_text
        assert stored_review.date_read == new_date_read
        assert stored_review.did_not_finish == new_did_not_finish
        assert stored_review.is_favourite == new_is_favourite

    def test_editing_non_existent_review_is_404(
        self, client, session, logged_in_user, review, fake
    ):
        csrf_token = helpers.get_csrf_token(client, path=f"/reviews/{review.id}")

        resp = client.post(
            "/edit-review",
            data={
                "csrf_token": csrf_token,
                "review_id": review.id + 1,
                "review_text": fake.text(),
                "date_read": fake.date_object().isoformat(),
                "did_not_finish": fake.boolean(),
                "is_favourite": fake.boolean(),
            },
        )

        assert resp.status_code == 404

    def test_can_edit_plan(self, client, session, logged_in_user, plan, fake):
        new_note = fake.text()
        new_date_added = fake.date_object()

        assert plan.note != new_note
        assert plan.date_added != new_date_added

        csrf_token = helpers.get_csrf_token(client, path="/to-read")

        resp = client.post(
            f"/edit-plan/{plan.id}",
            data={
                "csrf_token": csrf_token,
                "note": new_note,
                "date_added": new_date_added.isoformat(),
            },
        )

        assert helpers.is_redirect(resp, location=f"/to-read#plan-{plan.id}")

        stored_plan = Plan.query.get(plan.id)

        assert stored_plan.note == new_note
        assert stored_plan.date_added == new_date_added

        resp = client.get("/to-read")
        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        html_plan = soup.find("div", attrs={"id": f"plan-{plan.id}"})
        assert html_plan is not None

        book_title = html_plan.find("h3", attrs={"class": "book-title"})
        assert book_title.text.strip() == plan.book.title

    def test_editing_non_existent_plan_is_404(
        self, client, session, logged_in_user, fake
    ):
        csrf_token = helpers.get_csrf_token(client, path="/to-read")

        resp = client.post(
            f"/edit-plan/1",
            data={
                "csrf_token": csrf_token,
                "note": fake.text(),
                "date_added": fake.date_object().isoformat(),
            },
        )

        assert resp.status_code == 404

    def test_can_edit_reading(self, client, session, logged_in_user, reading, fake):
        new_note = fake.text()

        assert reading.note != new_note

        csrf_token = helpers.get_csrf_token(client, path="/reading")

        resp = client.post(
            f"/edit-reading/{reading.id}",
            data={"csrf_token": csrf_token, "note": new_note},
        )

        assert helpers.is_redirect(resp, location=f"/reading#reading-{reading.id}")

        stored_reading = Reading.query.get(reading.id)

        assert stored_reading.note == new_note

        resp = client.get("/reading")
        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        html_reading = soup.find("div", attrs={"id": f"reading-{reading.id}"})
        assert html_reading is not None

        book_title = html_reading.find("h3", attrs={"class": "book-title"})
        assert book_title.text.strip() == reading.book.title

    def test_editing_non_existent_reading_is_404(
        self, client, session, logged_in_user, fake
    ):
        csrf_token = helpers.get_csrf_token(client, path="/reading")

        resp = client.post(
            f"/edit-reading/1", data={"csrf_token": csrf_token, "note": fake.text()}
        )

        assert resp.status_code == 404
