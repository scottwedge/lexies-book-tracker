# -*- encoding: utf-8

import datetime as dt
import json
import pathlib

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import scss
import smartypants

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.jinja_env.filters["to_json"] = json.dumps
app.jinja_env.filters["smartypants"] = smartypants.smartypants

login = LoginManager(app)
login.login_view = "login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import routes  # noqa
from .models import User  # noqa


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.template_filter("render_date")
def render_date(date_val):
    delta = dt.datetime.now().date() - date_val

    if delta.days == 0:
        return "today"
    elif delta.days == 1:
        return "yesterday"
    elif delta.days <= 7:
        return f"{delta.days} days ago"
    else:
        return date_val.strftime("%d %B %Y")


@app.before_first_request
def compile_css():
    print("Rebuilding CSS")
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    css = scss.Compiler(root=src_root / "assets").compile("style.scss")

    css_path = static_dir / "style.css"
    css_path.write_text(css)
