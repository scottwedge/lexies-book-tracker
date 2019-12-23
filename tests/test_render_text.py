# -*- encoding: utf-8

import pytest

from src import render_text


@pytest.mark.parametrize(
    "source_text, expected_html",
    [
        ("hello world", "hello world"),
        ("isn't this nice?", "isn&#8217;t this nice?"),
        (
            "This is a URL: https://example.net",
            'This is a URL: <a href="https://example.net">https://example.net</a>',
        ),
        (
            "This is an HTTP URL: http://example.net",
            'This is an HTTP URL: <a href="http://example.net">http://example.net</a>',
        ),
        (
            "This is a string with multiple URLs: https://example.net/path/to/resource http://example.org/another/resource?t=123",
            'This is a string with multiple URLs: <a href="https://example.net/path/to/resource">https://example.net/path/to/resource</a> <a href="http://example.org/another/resource?t=123">http://example.org/another/resource?t=123</a>',
        ),
    ],
)
def test_render_text(source_text, expected_html):
    assert render_text(source_text) == expected_html
