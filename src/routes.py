# -*- encoding: utf-8

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src import app, db
from src.booksearch import lookup_google_books
from src.forms import EditReviewForm, LoginForm, RegistrationForm, ReviewForm
from src.models import Book, Review, User


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template(
        "reviews.html",
        reviews=[
            "This book was good.",
            "This book was also good.",
            "This book was bad.",
        ],
    )


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
            image_url=image_url
        )
        db.session.add(new_book)
        db.session.commit()
        return new_book


def save_review(*, review, date_read, did_not_finish, is_favourite, book, user):
    review = Review(
        review=review,
        date_read=date_read,
        did_not_finish=did_not_finish,
        is_favourite=is_favourite,
        book_id=book.id,
        user_id=user.id,
    )
    db.session.add(review)
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
                review=review_form.review.data,
                date_read=review_form.date_read.data,
                did_not_finish=review_form.did_not_finish.data,
                is_favourite=review_form.is_favourite.data,
                book=book,
                user=user
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
                id=edit_form.review_id.data,
                user_id=user.id).first_or_404()

            review.review = edit_form.review.data
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


@app.route("/user/<username>", methods=["GET", "POST"])
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


@app.route("/user/<username>/reviews/<review_id>")
def get_review(username, review_id):
    pass


@app.route("/booksearch")
def search_books():
    search_query = request.args["search"]

    lookup_result = lookup_google_books(
        api_key=app.config["GOOGLE_BOOKS_API_KEY"],
        search_query=search_query
    )

    return jsonify({"books": lookup_result})


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Unrecognised username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))
    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email_address=form.email_address.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)
