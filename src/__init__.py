# -*- encoding: utf-8

import json
import pathlib

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import scss
from scss.types import Color

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.jinja_env.filters["to_json"] = json.dumps

login = LoginManager(app)
login.login_view = "login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import routes
from .models import User


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_first_request
def compile_css():
    print("Rebuilding CSS")
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    css = scss.Compiler(root=src_root / "assets").compile("style.scss")

    css_path = static_dir / "style.css"
    css_path.write_text(css)
