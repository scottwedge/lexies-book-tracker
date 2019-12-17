# -*- encoding: utf-8

import os
import pathlib


basedir = pathlib.Path(__file__).parent.resolve()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    try:
        SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    except KeyError:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir}/app.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
