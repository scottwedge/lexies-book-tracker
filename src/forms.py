# -*- encoding: utf-8

import datetime

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User


def today():
    return datetime.datetime.now().date()


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    remember_me = BooleanField("remember me?")
    submit = SubmitField("sign in")


class BookFormMixin:
    title = StringField("title", validators=[DataRequired()])
    author = StringField("author")
    year = StringField("year")
    identifiers = StringField("identifiers")
    source_id = StringField("source_id")
    image_url = StringField("image_url")
    isbn_10 = StringField("isbn_10")
    isbn_13 = StringField("isbn_13")


class ReviewFormMixin:
    review_text = TextAreaField("review")
    date_read = DateField("date read", default=today)
    did_not_finish = BooleanField("didn’t finish 😔", default=False)
    is_favourite = BooleanField("loved it! 😍", default=False)


class ReviewForm(ReviewFormMixin, BookFormMixin, FlaskForm):
    pass


class EditReviewForm(ReviewFormMixin, FlaskForm):
    review_id = IntegerField("id", validators=[DataRequired()])


class ReadingFormMixin:
    note = TextAreaField("note")


class ReadingForm(ReadingFormMixin, BookFormMixin, FlaskForm):
    pass


class EditReadingForm(ReadingFormMixin, FlaskForm):
    pass


class MarkAsReadForm(ReviewFormMixin, FlaskForm):
    pass


class PlanFormMixin:
    note = TextAreaField("note")
    date_added = DateField("date_added", default=today)


class PlanForm(PlanFormMixin, BookFormMixin, FlaskForm):
    pass


class EditPlanForm(PlanFormMixin, FlaskForm):
    pass
