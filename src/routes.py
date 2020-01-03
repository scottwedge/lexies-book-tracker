# -*- encoding: utf-8

import hashlib
from urllib.parse import unquote_plus

from flask import (
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
import requests

from . import app, db
from .booksearch import lookup_google_books
from .forms import (
    ReadingForm,
    EditReadingForm,
    EditReviewForm,
    EditPlanForm,
    LoginForm,
    MarkAsReadForm,
    PlanForm,
    ReviewForm,
)
from .models import Book, Reading, Plan, Review, User


def md5(s):
    h = hashlib.md5()
    h.update(s.encode("utf8"))
    return h.hexdigest()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add-review", methods=["POST"])
def add_review():
    user = User.query.get(1)

    if current_user == user:
        review_form = ReviewForm()

        if review_form.validate_on_submit():
            book = Book.create_or_get(
                title=review_form.title.data,
                author=review_form.author.data,
                year=review_form.year.data,
                identifiers=review_form.identifiers.data,
                source_id=review_form.source_id.data,
                image_url=review_form.image_url.data,
                isbn_10=review_form.isbn_10.data,
                isbn_13=review_form.isbn_13.data,
            )
            Review.create(
                review_text=review_form.review_text.data,
                date_read=review_form.date_read.data,
                did_not_finish=review_form.did_not_finish.data,
                is_favourite=review_form.is_favourite.data,
                book=book,
                user=user,
            )
        else:
            abort(400)

        return redirect(url_for("list_reviews"))
    else:
        abort(401)


@app.route("/edit-review", methods=["POST"])
def edit_review():
    user = User.query.get(1)

    if current_user == user:
        edit_form = EditReviewForm()

        if edit_form.validate_on_submit():
            review = Review.query.filter_by(
                id=edit_form.review_id.data, user_id=user.id
            ).first_or_404()

            review.review_text = edit_form.review_text.data
            review.date_read = edit_form.date_read.data
            review.did_not_finish = edit_form.did_not_finish.data
            review.is_favourite = edit_form.is_favourite.data
            db.session.commit()
        else:
            abort(400)

        return redirect(url_for("get_review", review_id=review.id))
    else:
        abort(401)


@app.route("/delete-review/<review_id>", methods=["POST"])
def delete_review(review_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    review = Review.query.filter_by(id=review_id, user_id=user.id).first_or_404()

    db.session.delete(review)
    db.session.commit()

    return redirect(url_for("list_reviews"))


@app.route("/read")
def list_reviews():
    user = User.query.get(1)

    if current_user == user:
        review_form = ReviewForm()
        edit_form = EditReviewForm()
    else:
        review_form = None
        edit_form = None

    return render_template(
        "reviews.html",
        user=user,
        reviews=user.reviews.order_by(Review.date_read.desc()).all(),
        review_form=review_form,
        edit_form=edit_form,
        title=f"my books",
    )


@app.route("/reviews/<review_id>")
def get_review(review_id):
    review = Review.query.filter_by(id=int(review_id)).first_or_404()

    user = User.query.get(1)

    if current_user == user:
        review_form = ReviewForm()
        edit_form = EditReviewForm()
    else:
        review_form = None
        edit_form = None

    return render_template(
        "reviews.html",
        user=user,
        reviews=[review],
        review_form=review_form,
        edit_form=edit_form,
        title=f"my review of {review.book.title}",
        show_reviews=True,
    )


@app.route("/reading")
def list_reading():
    user = User.query.get(1)

    if current_user == user:
        reading_form = ReadingForm()
        review_form = ReviewForm()
        edit_form = EditReadingForm()
    else:
        reading_form = None
        review_form = None
        edit_form = None

    return render_template(
        "reading.html",
        user=user,
        currently_reading=user.reading.all(),
        reading_form=reading_form,
        review_form=review_form,
        edit_form=edit_form,
        title=f"what i’m reading",
    )


@app.route("/to-read")
def list_plans():
    user = User.query.get(1)

    if current_user == user:
        plan_form = PlanForm()
        review_form = ReviewForm()
        edit_form = EditPlanForm()
    else:
        plan_form = None
        review_form = None
        edit_form = None

    return render_template(
        "plans.html",
        user=user,
        plans=user.plans.all(),
        plan_form=plan_form,
        review_form=review_form,
        edit_form=edit_form,
        title=f"what i want to read",
    )


@app.route("/add-plan", methods=["POST"])
def add_plan():
    user = User.query.get(1)

    if current_user != user:
        return abort(401)

    plan_form = PlanForm()

    if plan_form.validate_on_submit():
        book = Book.create_or_get(
            title=plan_form.title.data,
            author=plan_form.author.data,
            year=plan_form.year.data,
            identifiers=plan_form.identifiers.data,
            source_id=plan_form.source_id.data,
            image_url=plan_form.image_url.data,
            isbn_10=plan_form.isbn_10.data,
            isbn_13=plan_form.isbn_13.data,
        )
        Plan.create(
            note=plan_form.note.data, book=book, user=user,
        )

    return redirect(url_for("list_plans"))


@app.route("/edit-reading/<reading_id>", methods=["POST"])
def edit_reading(reading_id):
    user = User.query.get(1)

    if current_user == user:
        edit_form = EditReadingForm()

        if edit_form.validate_on_submit():
            reading = Reading.query.filter_by(
                id=reading_id, user_id=user.id
            ).first_or_404()

            reading.note = edit_form.note.data
            db.session.commit()

        return redirect(url_for("list_reading"))
    else:
        abort(401)


@app.route("/edit-plan/<plan_id>", methods=["POST"])
def edit_plan(plan_id):
    user = User.query.get(1)

    if current_user == user:
        edit_form = EditPlanForm()

        if edit_form.validate_on_submit():
            plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

            plan.note = edit_form.note.data
            plan.date_added = edit_form.date_added.data
            db.session.commit()

        return redirect(url_for("list_plans"))
    else:
        abort(401)


@app.route("/add-reading", methods=["POST"])
def add_reading():
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    reading_form = ReadingForm()

    book = Book.create_or_get(
        title=reading_form.title.data,
        author=reading_form.author.data,
        year=reading_form.year.data,
        identifiers=reading_form.identifiers.data,
        source_id=reading_form.source_id.data,
        image_url=reading_form.image_url.data,
        isbn_10=reading_form.isbn_10.data,
        isbn_13=reading_form.isbn_13.data,
    )

    Reading.create(note=reading_form.note.data, book=book, user=user)

    return redirect(url_for("list_reading"))


@app.route("/delete-reading/<reading_id>", methods=["POST"])
def delete_reading(reading_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    reading = Reading.query.filter_by(id=reading_id, user_id=user.id).first_or_404()

    db.session.delete(reading)
    db.session.commit()

    return redirect(url_for("list_reading"))


@app.route("/delete-plan/<plan_id>", methods=["POST"])
def delete_plan(username, plan_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    db.session.delete(plan)
    db.session.commit()

    return redirect(url_for("list_plans"))


@app.route("/mark_as_read/<reading_id>", methods=["POST"])
def mark_as_read(reading_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    reading = Reading.query.filter_by(id=reading_id, user_id=user.id).first_or_404()

    mark_as_read_form = MarkAsReadForm()

    if mark_as_read_form.validate_on_submit():
        flash(f"Marking {reading.book.title} as read")
        reading.mark_as_read(
            review_text=mark_as_read_form.review_text.data,
            date_read=mark_as_read_form.date_read.data,
            did_not_finish=mark_as_read_form.did_not_finish.data,
            is_favourite=mark_as_read_form.is_favourite.data,
        )

    return redirect(url_for("list_reviews"))


@app.route("/mark_plan_as_read/<plan_id>", methods=["POST"])
def mark_plan_as_read(plan_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    mark_as_read_form = MarkAsReadForm()

    if mark_as_read_form.validate_on_submit():
        flash(f"Marking {plan.book.title} as read")
        plan.mark_as_read(
            review_text=mark_as_read_form.review_text.data,
            date_read=mark_as_read_form.date_read.data,
            did_not_finish=mark_as_read_form.did_not_finish.data,
            is_favourite=mark_as_read_form.is_favourite.data,
        )

    return redirect(url_for("list_reviews"))


@app.route("/move_plan_to_reading/<plan_id>", methods=["POST"])
def move_plan_to_reading(plan_id):
    user = User.query.get(1)

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    flash(f"You have started reading {plan.book.title}")
    plan.mark_as_reading()

    return redirect(url_for("list_reading"))


@app.route("/booksearch")
@login_required
def search_books():
    search_query = request.args["search"]

    lookup_result = lookup_google_books(
        api_key=app.config["GOOGLE_BOOKS_API_KEY"], search_query=search_query
    )

    return jsonify({"books": lookup_result})


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("list_reviews"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Unrecognised username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("list_reviews", username=user.username))
    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/proxy/<url>")
def proxy(url):
    """
    When loading images, we have two issues with loading them directly from
    the source URL:

    1.  CORS headers on my web server are pretty restrictive
    2.  Sources may not set the correct caching headers, so the browser reloads
        all the images at once!

    This proxy method intercepts a URL it receives, adds long caching headers,
    then returns the original data.

    Because browsers only cache on the basis of paths, not query parameters,
    the URL is supplied as a URL-encoded path component.

    """
    url = unquote_plus(url)

    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.HTTPError as err:
        print(err)
        return abort(400)

    headers_to_keep = {
        "content-type",
        "content-length",
    }

    headers = {
        name: value
        for (name, value) in resp.raw.headers.items()
        if name.lower() in headers_to_keep
    }

    if resp.status_code == 200:
        headers["Cache-Control"] = "public, max-age=31536000"
        headers["ETag"] = md5(url)

    return Response(response=resp.content, status=resp.status_code, headers=headers)
