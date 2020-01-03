import bs4


def test_can_be_logged_in(client, logged_in_user):
    resp = client.get("/")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    top_items = soup.find("aside").find_all("li")

    assert top_items[0].text == "home"
    assert top_items[1].text.strip().startswith(f"logged in as {logged_in_user.username}")
