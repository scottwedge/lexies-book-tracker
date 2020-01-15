import bs4

import helpers


def test_can_be_logged_in(client, logged_in_user):
    resp = client.get("/")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    top_items = soup.find("aside").find_all("li")

    assert top_items[0].text == "home"
    assert (
        top_items[1].text.strip().startswith(f"logged in as {logged_in_user.username}")
    )


def test_can_log_out(client, logged_in_user):
    client.get("/logout")

    resp = client.get("/")
    assert b"logged in as" not in resp.data


def test_already_logged_in_user_goes_to_reviews(client, logged_in_user):
    resp = client.get("/login")

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/read")


def test_logging_in_as_unknown_user_is_error(client, session):
    csrf_token = helpers.get_csrf_token(client, path="/login")

    resp = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "username": "doesnotexist",
            "password": "sekritsekrit",
        },
    )

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    resp = client.get("/login")
    assert b"Unrecognised username or password" in resp.data


def test_logging_in_with_wrong_password_is_error(client, session, user):
    user.set_password("sekrit")
    session.commit()

    csrf_token = helpers.get_csrf_token(client, path="/login")

    resp = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "username": user.username,
            "password": "wrongpassword",
        },
    )

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    resp = client.get("/login")
    assert b"Unrecognised username or password" in resp.data
