from src.models import Reading


def test_can_delete_reading(client, session, logged_in_user, reading):
    resp = client.post(f"/delete-reading/{reading.id}")

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/reading")

    assert Reading.query.get(reading.id) is None


def test_cannot_delete_non_existent_reading(client, session, logged_in_user):
    resp = client.post(f"/delete-reading/1")

    assert resp.status_code == 404


def test_cannot_delete_reading_if_not_logged_in(client, session, reading):
    client.post("/logout")
    resp = client.post(f"/delete-reading/{reading.id}")

    assert resp.status_code == 401
