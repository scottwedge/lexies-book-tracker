# -*- encoding: utf-8
"""
Tests for the use of Smartypants and curly quotes throughout.
"""

import bs4
from flask import url_for

from src.models import Plan


def test_reading_page_title_is_curly_quotes(client, user):
    resp = client.get("/reading")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    assert soup.find("title").text == "what i’m reading 📚 lexie’s book tracker"
