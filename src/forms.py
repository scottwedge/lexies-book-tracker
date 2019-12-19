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


class RegistrationForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    email_address = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    password2 = PasswordField(
        "repeat password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email_address):
        user = User.query.filter_by(email_address=email_address.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class BookFormMixin:
    title = StringField("title", validators=[DataRequired()])
    author = StringField("author")
    year = StringField("year")
    identifiers = StringField("identifiers")
    source_id = StringField("source_id")
    image_url = StringField("image_url")


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
