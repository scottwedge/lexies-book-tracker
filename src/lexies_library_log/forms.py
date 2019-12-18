# -*- encoding: utf-8

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User, today


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
    isbn_13 = StringField("isbn_13")
    source_id = StringField("source_id")
    image_url = StringField("image_url")


class ReviewFormMixin:
    review_text = TextAreaField("review_text")
    date_read = DateField("date_read", default=today)
    did_not_finish = BooleanField("did_not_finish", default=False)
    is_favourite = BooleanField("is_favourite", default=False)


class ReviewForm(ReviewFormMixin, BookFormMixin, FlaskForm):
    pass


class EditReviewForm(ReviewFormMixin, FlaskForm):
    review_id = IntegerField("id", validators=[DataRequired()])


class CurrentlyReadingFormMixin:
    note = TextAreaField("note")


class CurrentlyReadingForm(CurrentlyReadingFormMixin, BookFormMixin, FlaskForm):
    pass


class EditCurrentlyReadingForm(CurrentlyReadingFormMixin, FlaskForm):
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
