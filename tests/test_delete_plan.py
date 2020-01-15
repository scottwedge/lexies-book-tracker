from src.models import Plan


def test_can_delete_plan(client, session, logged_in_user, plan):
    resp = client.post(f"/delete-plan/{plan.id}")

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/to-read")

    assert Plan.query.get(plan.id) is None


def test_cannot_delete_non_existent_plan(client, session, logged_in_user):
    resp = client.post(f"/delete-plan/1")

    assert resp.status_code == 404


def test_cannot_delete_plan_if_not_logged_in(client, session, plan):
    client.post("/logout")
    resp = client.post(f"/delete-plan/{plan.id}")

    assert resp.status_code == 401
