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


def test_plan_page_is_curly_quotes(client, book, user):
    book_title = "Old Possum’s Book of Practical Cats"
    note_text = "This is a book I haven’t read yet"

    book.title = book_title

    plan = Plan.create(
        note=note_text,
        book=book,
        user=user
    )

    resp = client.get("/to-read")
    soup = bs4.BeautifulSoup(resp.data, "html.parser")

    book_div = soup.find("div", attrs={"class": "book"})

    assert book_div.find("h3", attrs={"class": "book-title"}).text.strip() == book_title
    assert book_div.find("div", attrs={"class": "plan-note"}).text.strip() == note_text
