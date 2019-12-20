# -*- encoding: utf-8

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from src import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    reviews = db.relationship("Review", backref="user", lazy="dynamic")
    reading = db.relationship("Reading", backref="user", lazy="dynamic")
    plans = db.relationship("Plan", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username!r}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
