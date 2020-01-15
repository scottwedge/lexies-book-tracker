import pytest


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
