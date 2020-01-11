from src import render_text

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
    ],
)
def test_render_text(source_text, expected_text):
    assert render_text(source_text) == expected_text
