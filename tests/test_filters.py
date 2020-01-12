import datetime as dt

from src import render_date, render_text

import pytest


@pytest.mark.parametrize(
    "source_text, expected_text",
    [
        ("This is plain text", "This is plain text"),
        (
            "Isn't it cool how punctuation -- curly quotes, dashes, &c -- get HTML-ified?",
            "Isn&#8217;t it cool how punctuation &#8212; curly quotes, dashes, &c &#8212; get HTML-ified?",
        ),
        (
            "This has a link: https://example.org",
            'This has a link: <a href="https://example.org">https://example.org</a>',
        ),
        (
            "This link is in parens (https://example.org)",
            'This link is in parens (<a href="https://example.org">https://example.org</a>)',
        ),
        (
            "This link is in parens (https://example.org/my_file), and then another clause",
            'This link is in parens (<a href="https://example.org/my_file">https://example.org/my_file</a>), and then another clause',
        ),
    ],
)
def test_render_text(source_text, expected_text):
    assert render_text(source_text) == expected_text


@pytest.mark.parametrize(
    "date_val, expected_text",
    [
        (dt.datetime.now(), "today"),
        (dt.datetime.now() - dt.timedelta(days=1), "yesterday"),
        (dt.datetime.now() - dt.timedelta(days=5), "5 days ago"),
        (dt.datetime.now() - dt.timedelta(days=7), "7 days ago"),
        (dt.datetime(2019, 12, 1), "1 December 2019"),
    ],
)
def test_render_date(date_val, expected_text):
    assert render_date(date_val.date()) == expected_text
