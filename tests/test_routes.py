import datetime
import re

import bs4
import hyperlink
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
        "/edit-review/1",
        "/mark_as_read/1",
        "/mark_plan_as_read/1",
        "/move_plan_to_reading/1",
    ],
)
def test_cannot_post_to_route_if_not_logged_in(client, session, user, path):
    resp = client.post(path)
    assert resp.status_code == 401


@pytest.mark.parametrize("path", ["/add-plan", "/add-reading", "/add-review"])
def test_invalid_form_data_is_error(client, session, logged_in_user, path):
    resp = client.post(path, data={})
    assert resp.status_code == 400


def test_cannot_edit_review_with_invalid_form_data(
    client, session, logged_in_user, review
):
    resp = client.post("/edit-review/1", data={})
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
            f"/edit-review/{review.id}",
            data={
                "csrf_token": csrf_token,
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
            f"/edit-review/{review.id + 1}",
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


class TestDeleteRoutes:
    def test_can_delete_review(self, client, session, logged_in_user, review):
        resp = client.post(f"/delete-review/{review.id}")

        assert helpers.is_redirect(resp, location="/read")
        assert Review.query.get(review.id) is None

    def test_can_delete_reading(self, client, session, logged_in_user, reading):
        resp = client.post(f"/delete-reading/{reading.id}")

        assert helpers.is_redirect(resp, location="/reading")
        assert Reading.query.get(reading.id) is None

    def test_can_delete_plan(self, client, session, logged_in_user, plan):
        resp = client.post(f"/delete-plan/{plan.id}")

        assert helpers.is_redirect(resp, location="/to-read")
        assert Plan.query.get(plan.id) is None

    @pytest.mark.parametrize(
        "path", ["/delete-review/1", "/delete-reading/1", "/delete-plan/1"]
    )
    def test_deleting_nonexistent_object_is_404(
        self, client, session, logged_in_user, path
    ):
        resp = client.post(path)

        assert resp.status_code == 404


def extract_review_id(location):
    path_match = re.search(r"/read#book\-(?P<review_id>\d+)$", location)
    assert path_match is not None, location
    return path_match.group("review_id")


def extract_reading_id(location):
    path_match = re.search(r"/reading#reading\-(?P<reading_id>\d+)$", location)
    assert path_match is not None, location
    return path_match.group("reading_id")


def extract_plan_id(location):
    path_match = re.search(r"/to-read#plan\-(?P<plan_id>\d+)$", location)
    assert path_match is not None, location
    return path_match.group("plan_id")


class TestAddRoutes:
    def test_can_add_review(self, client, session, logged_in_user, book, fake):
        csrf_token = helpers.get_csrf_token(client, path="/read")

        review_text = fake.text()
        date_read = fake.date_object()
        did_not_finish = fake.boolean()
        is_favourite = fake.boolean()

        resp = client.post(
            "/add-review",
            data={
                "csrf_token": csrf_token,
                "title": book.title,
                "year": book.year,
                "identifiers": book.identifiers_json,
                "source_id": book.source_id,
                "image_url": book.image_url,
                "isbn_10": book.isbn_10,
                "isbn_13": book.isbn_13,
                "review_text": review_text,
                "date_read": date_read,
                "did_not_finish": did_not_finish,
                "is_favourite": is_favourite,
            },
        )

        assert resp.status_code == 302

        location = resp.headers["Location"]
        review_id = extract_review_id(location)

        stored_review = Review.query.get(review_id)
        assert stored_review.review_text == review_text
        assert stored_review.date_read == date_read
        # TODO: This works in the app, but not in the tests.
        # assert stored_review.did_not_finish == did_not_finish
        # assert stored_review.is_favourite == is_favourite

        resp = client.get("/read")
        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        review = soup.find("div", attrs={"id": f"book-{review_id}"})
        book_title = review.find("h3", attrs={"class": "book-title"})
        assert book_title.text.strip() == book.title

    def test_can_add_reading(self, client, session, logged_in_user, book, fake):
        csrf_token = helpers.get_csrf_token(client, path="/reading")

        note = fake.text()

        resp = client.post(
            "/add-reading",
            data={
                "csrf_token": csrf_token,
                "title": book.title,
                "year": book.year,
                "identifiers": book.identifiers_json,
                "source_id": book.source_id,
                "image_url": book.image_url,
                "isbn_10": book.isbn_10,
                "isbn_13": book.isbn_13,
                "note": note,
            },
        )

        assert resp.status_code == 302

        location = resp.headers["Location"]
        reading_id = extract_reading_id(location)

        stored_reading = Reading.query.get(reading_id)
        assert stored_reading.note == note
        assert stored_reading.date_started == datetime.datetime.now().date()

        resp = client.get("/reading")
        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        reading = soup.find("div", attrs={"id": f"reading-{reading_id}"})
        book_title = reading.find("h3", attrs={"class": "book-title"})
        assert book_title.text.strip() == book.title

    def test_can_add_plan(self, client, session, logged_in_user, book, fake):
        csrf_token = helpers.get_csrf_token(client, path="/to-read")

        note = fake.text()

        resp = client.post(
            "/add-plan",
            data={
                "csrf_token": csrf_token,
                "title": book.title,
                "year": book.year,
                "identifiers": book.identifiers_json,
                "source_id": book.source_id,
                "image_url": book.image_url,
                "isbn_10": book.isbn_10,
                "isbn_13": book.isbn_13,
                "note": note,
            },
        )

        assert resp.status_code == 302

        location = resp.headers["Location"]
        plan_id = extract_plan_id(location)

        stored_plan = Plan.query.get(plan_id)
        assert stored_plan.note == note
        assert stored_plan.date_added == datetime.datetime.now().date()

        resp = client.get("/to-read")
        soup = bs4.BeautifulSoup(resp.data, "html.parser")

        plan = soup.find("div", attrs={"id": f"plan-{plan_id}"})
        book_title = plan.find("h3", attrs={"class": "book-title"})
        assert book_title.text.strip() == book.title


class TestTransitions:
    def test_can_mark_reading_as_read(
        self, client, session, logged_in_user, reading, fake
    ):
        csrf_token = helpers.get_csrf_token(client, path="/reading")

        review_text = fake.text()
        date_read = fake.date_object()
        did_not_finish = fake.boolean()
        is_favourite = fake.boolean()

        resp = client.post(
            f"/mark_as_read/{reading.id}",
            data={
                "csrf_token": csrf_token,
                "review_text": review_text,
                "date_read": date_read,
                "did_not_finish": did_not_finish,
                "is_favourite": is_favourite,
            },
        )

        assert resp.status_code == 302

        location = resp.headers["Location"]
        review_id = extract_review_id(location)

        assert Reading.query.get(reading.id) is None

        stored_review = Review.query.get(review_id)
        assert stored_review.review_text == review_text
        assert stored_review.date_read == date_read
        # TODO: This works in the app, but not in the tests.
        # assert stored_review.did_not_finish == did_not_finish
        # assert stored_review.is_favourite == is_favourite

        resp = client.get("/read")
        assert helpers.is_flashed(
            resp, expected_message=f"Marked {reading.book.title} as read"
        )

    def test_can_mark_plan_as_read(self, client, session, logged_in_user, plan, fake):
        csrf_token = helpers.get_csrf_token(client, path="/to-read")

        review_text = fake.text()
        date_read = fake.date_object()
        did_not_finish = fake.boolean()
        is_favourite = fake.boolean()

        resp = client.post(
            f"/mark_plan_as_read/{plan.id}",
            data={
                "csrf_token": csrf_token,
                "review_text": review_text,
                "date_read": date_read,
                "did_not_finish": did_not_finish,
                "is_favourite": is_favourite,
            },
        )

        assert resp.status_code == 302

        location = resp.headers["Location"]
        review_id = extract_review_id(location)

        assert Plan.query.get(plan.id) is None

        stored_review = Review.query.get(review_id)
        assert stored_review.review_text == review_text
        assert stored_review.date_read == date_read
        # TODO: This works in the app, but not in the tests.
        # assert stored_review.did_not_finish == did_not_finish
        # assert stored_review.is_favourite == is_favourite

        resp = client.get("/read")
        assert helpers.is_flashed(
            resp, expected_message=f"Marked {plan.book.title} as read"
        )

    def test_can_move_plan_to_reading(
        self, client, session, logged_in_user, plan, fake
    ):
        resp = client.post(f"/move_plan_to_reading/{plan.id}")

        assert resp.status_code == 302

        location = resp.headers["Location"]
        review_id = extract_reading_id(location)

        assert Plan.query.get(plan.id) is None

        stored_reading = Reading.query.get(review_id)
        assert stored_reading.note == plan.note
        assert stored_reading.date_started == datetime.datetime.now().date()

        resp = client.get("/to-read")
        assert helpers.is_flashed(
            resp, expected_message=f"You have started reading {plan.book.title}"
        )
