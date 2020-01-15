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
