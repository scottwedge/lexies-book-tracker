import bs4


def test_can_get_plan_page(client, session, logged_in_user):
    resp = client.get("/to-read")

    assert b"I don&rsquo;t have anything I want to read right now!" in resp.data


def test_no_add_plan_form_if_not_logged_in(client, session, user):
    resp = client.get("/to-read")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    assert soup.find("div", attrs={"book-add-form"}) is None
