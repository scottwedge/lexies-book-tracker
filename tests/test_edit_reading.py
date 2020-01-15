import datetime

import helpers
from src.models import Reading


def test_can_edit_reading(client, session, logged_in_user, reading, fake):
    new_note = fake.text()

    assert new_note != reading.note

    resp = client.get(f"/to-read")
    csrf_token = helpers.get_csrf_token(resp.data)

    edit_reading_resp = client.post(f"/edit-reading/{reading.id}", data={
        "csrf_token": csrf_token,
        "note": new_note,
    })

    assert edit_reading_resp.status_code == 302
    assert edit_reading_resp.headers["Location"].endswith(f"/reading#{reading.id}")

    stored_reading = Reading.query.get(reading.id)
    assert stored_reading.note == new_note


def test_malformed_edit_reading_form_is_error(client, session, logged_in_user):
    resp = client.post("/edit-reading/1", data={})
    assert resp.status_code == 400


def test_cannot_edit_reading_if_not_logged_in(client, session):
    resp = client.post("/edit-reading/1")
    assert resp.status_code == 401
