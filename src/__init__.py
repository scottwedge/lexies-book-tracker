# -*- encoding: utf-8

import json

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
