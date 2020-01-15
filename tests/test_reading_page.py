import bs4


def test_can_get_reading_page(client, session, logged_in_user):
    resp = client.get("/reading")

    assert b"I&rsquo;m not reading any books right now!" in resp.data


def test_no_add_reading_form_if_not_logged_in(client, session, user):
    resp = client.get("/reading")

    soup = bs4.BeautifulSoup(resp.data, "html.parser")
    assert soup.find("div", attrs={"book-add-form"}) is None
