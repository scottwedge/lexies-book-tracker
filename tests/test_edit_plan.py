import datetime

import helpers
from src.models import Plan


def test_can_edit_plan(client, session, logged_in_user, plan, fake):
    new_note = fake.text()
    date_added = (datetime.datetime.now() - datetime.timedelta(days=7)).date()

    assert new_note != plan.note
    assert date_added != plan.date_added

    resp = client.get(f"/to-read")
    csrf_token = helpers.get_csrf_token(resp.data)

    edit_plan_resp = client.post(f"/edit-plan/{plan.id}", data={
        "csrf_token": csrf_token,
        "note": new_note,
        "date_added": date_added.isoformat(),
    })

    assert edit_plan_resp.status_code == 302
    assert edit_plan_resp.headers["Location"].endswith(f"/to-read#{plan.id}")

    stored_plan = Plan.query.get(plan.id)
    assert stored_plan.note == new_note


def test_malformed_edit_plan_form_is_error(client, session, logged_in_user):
    resp = client.post("/edit-plan/1", data={})
    assert resp.status_code == 400


def test_cannot_edit_plan_if_not_logged_in(client, session):
    resp = client.post("/edit-plan/1")
    assert resp.status_code == 401
