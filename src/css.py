# -*- encoding: utf-8

import pathlib

import scss
from scss.types import Color


def compile_css(accent_color):
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    css = scss.Compiler(root=src_root / "assets").compile("style.scss")
    print(css)

    css_path = static_dir / "style.css"
    css_path.write_text(css)
