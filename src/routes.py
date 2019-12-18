# -*- encoding: utf-8

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import app, db
from .booksearch import lookup_google_books
from .forms import (
    CurrentlyReadingForm,
    EditCurrentlyReadingForm,
    EditReviewForm,
    EditPlanForm,
    LoginForm,
    MarkAsReadForm,
    PlanForm,
    RegistrationForm,
    ReviewForm,
)
from .models import Book, CurrentlyReading, Plan, Review, User


@app.route("/")
@app.route("/index")
@login_required
def index():
    return "Welcome to Lexie's library log!"


def save_book(*, title, author, year, isbn_13, source_id, image_url):
    book = Book.query.filter_by(source_id=source_id).first()

    if book is not None:
        return book
    else:
        new_book = Book(
            title=title,
            author=author,
            year=year,
            isbn_13=isbn_13,
            source_id=source_id,
            image_url=image_url,
        )
        db.session.add(new_book)
        db.session.commit()
        return new_book


def save_review(*, review_text, date_read, did_not_finish, is_favourite, book, user):
    review = Review(
        review_text=review_text,
        date_read=date_read,
        did_not_finish=did_not_finish,
        is_favourite=is_favourite,
        book_id=book.id,
        user_id=user.id,
    )
    db.session.add(review)
    db.session.commit()


def save_currently_reading(*, note, book, user):
    currently_reading = CurrentlyReading(note=note, book_id=book.id, user_id=user.id,)
    db.session.add(currently_reading)
    db.session.commit()


@app.route("/user/<username>/add-review", methods=["POST"])
def add_review(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user == user:
        review_form = ReviewForm()

        if review_form.validate_on_submit():
            book = save_book(
                title=review_form.title.data,
                author=review_form.author.data,
                year=review_form.year.data,
                isbn_13=review_form.isbn_13.data,
                source_id=review_form.source_id.data,
                image_url=review_form.image_url.data,
            )
            save_review(
                review_text=review_form.review_text.data,
                date_read=review_form.date_read.data,
                did_not_finish=review_form.did_not_finish.data,
                is_favourite=review_form.is_favourite.data,
                book=book,
                user=user,
            )

        return redirect(url_for("get_reviews", username=username))
    else:
        abort(401)


@app.route("/user/<username>/edit-review", methods=["POST"])
def edit_review(username):
    user = User.query.filter_by(username=username).first_or_404()

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

        return redirect(url_for("get_reviews", username=username))
    else:
        abort(401)


@app.route("/user/<username>/delete-review/<review_id>", methods=["POST"])
def delete_review(username, review_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    review = Review.query.filter_by(id=review_id, user_id=user.id).first_or_404()

    db.session.delete(review)
    db.session.commit()

    return redirect(url_for("get_reviews", username=username))


@app.route("/user/<username>")
def get_reviews(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user == user:
        review_form = ReviewForm()
        edit_form = EditReviewForm()
    else:
        review_form = None
        edit_form = None

    return render_template(
        "reviews.html",
        user=user,
        reviews=user.reviews.all(),
        review_form=review_form,
        edit_form=edit_form,
    )


@app.route("/user/<username>/reading")
def get_reading(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user == user:
        reading_form = CurrentlyReadingForm()
        review_form = ReviewForm()
        edit_form = EditCurrentlyReadingForm()
    else:
        reading_form = None
        review_form = None
        edit_form = None

    return render_template(
        "reading.html",
        user=user,
        currently_reading=user.currently_reading.all(),
        reading_form=reading_form,
        review_form=review_form,
        edit_form=edit_form,
    )


@app.route("/user/<username>/to-read")
def get_plans(username):
    user = User.query.filter_by(username=username).first_or_404()

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
    )


@app.route("/user/<username>/add-plan", methods=["POST"])
def add_plan(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        return abort(401)

    plan_form = PlanForm()

    if plan_form.validate_on_submit():
        book = save_book(
            title=plan_form.title.data,
            author=plan_form.author.data,
            year=plan_form.year.data,
            isbn_13=plan_form.isbn_13.data,
            source_id=plan_form.source_id.data,
            image_url=plan_form.image_url.data,
        )
        save_plan(
            note=plan_form.note.data,
            date_added=plan_form.date_added.data,
            book=book,
            user=user,
        )

    return redirect(url_for("get_plans", username=username))


def save_plan(*, note, date_added, book, user):
    plan = Plan(note=note, date_added=date_added, book_id=book.id, user_id=user.id)

    db.session.add(plan)
    db.session.commit()


@app.route("/user/<username>/edit-reading/<reading_id>", methods=["POST"])
def edit_reading(username, reading_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user == user:
        edit_form = EditCurrentlyReadingForm()

        if edit_form.validate_on_submit():
            reading = CurrentlyReading.query.filter_by(
                id=reading_id, user_id=user.id
            ).first_or_404()

            reading.note = edit_form.note.data
            db.session.commit()

        return redirect(url_for("get_reading", username=username))
    else:
        abort(401)


@app.route("/user/<username>/edit-plan/<plan_id>", methods=["POST"])
def edit_plan(username, plan_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user == user:
        edit_form = EditPlanForm()

        if edit_form.validate_on_submit():
            plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

            plan.note = edit_form.note.data
            plan.date_added = edit_form.date_added.data
            db.session.commit()

        return redirect(url_for("get_plans", username=username))
    else:
        abort(401)


@app.route("/user/<username>/add-reading", methods=["POST"])
def add_reading(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    reading_form = CurrentlyReadingForm()

    book = save_book(
        title=reading_form.title.data,
        author=reading_form.author.data,
        year=reading_form.year.data,
        isbn_13=reading_form.isbn_13.data,
        source_id=reading_form.source_id.data,
        image_url=reading_form.image_url.data,
    )

    save_currently_reading(note=reading_form.note.data, book=book, user=user)

    return redirect(url_for("get_reading", username=username))


@app.route("/user/<username>/delete-reading/<reading_id>", methods=["POST"])
def delete_reading(username, reading_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    reading = CurrentlyReading.query.filter_by(
        id=reading_id, user_id=user.id
    ).first_or_404()

    db.session.delete(reading)
    db.session.commit()

    return redirect(url_for("get_reading", username=username))


@app.route("/user/<username>/delete-plan/<plan_id>", methods=["POST"])
def delete_plan(username, plan_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    db.session.delete(plan)
    db.session.commit()

    return redirect(url_for("get_plans", username=username))


@app.route("/user/<username>/mark_as_read/<reading_id>", methods=["POST"])
def mark_as_read(username, reading_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    reading = CurrentlyReading.query.filter_by(
        id=reading_id, user_id=user.id
    ).first_or_404()

    mark_as_read_form = MarkAsReadForm()

    if mark_as_read_form.validate_on_submit():
        flash(f"Marking {reading.book.title} as read")
        save_review(
            review_text=mark_as_read_form.review_text.data,
            date_read=mark_as_read_form.date_read.data,
            did_not_finish=mark_as_read_form.did_not_finish.data,
            is_favourite=mark_as_read_form.is_favourite.data,
            book=reading.book,
            user=user,
        )
        db.session.delete(reading)
        db.session.commit()

    return redirect(url_for("get_reviews", username=username))


@app.route("/user/<username>/mark_plan_as_read/<plan_id>", methods=["POST"])
def mark_plan_as_read(username, plan_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    mark_as_read_form = MarkAsReadForm()

    if mark_as_read_form.validate_on_submit():
        flash(f"Marking {plan.book.title} as read")
        save_review(
            review_text=mark_as_read_form.review_text.data,
            date_read=mark_as_read_form.date_read.data,
            did_not_finish=mark_as_read_form.did_not_finish.data,
            is_favourite=mark_as_read_form.is_favourite.data,
            book=plan.book,
            user=user,
        )
        db.session.delete(plan)
        db.session.commit()

    return redirect(url_for("get_reviews", username=username))


@app.route("/user/<username>/move_plan_to_reading/<plan_id>", methods=["POST"])
def move_plan_to_reading(username, plan_id):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user != user:
        abort(401)

    plan = Plan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()

    flash(f"You are reading {plan.book.title}")
    save_currently_reading(note=plan.note, book=plan.book, user=user)
    db.session.delete(plan)
    db.session.commit()

    return redirect(url_for("get_reading", username=username))


@app.route("/user/<username>/reviews/<review_id>")
def get_review(username, review_id):
    pass


@app.route("/booksearch")
def search_books():
    search_query = request.args["search"]

    lookup_result = lookup_google_books(
        api_key=app.config["GOOGLE_BOOKS_API_KEY"], search_query=search_query
    )

    return jsonify({"books": lookup_result})


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("get_reviews", username=current_user.username))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Unrecognised username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("get_reviews", username=user.username))
    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("get_reviews", username=current_user.username))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email_address=form.email_address.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)
