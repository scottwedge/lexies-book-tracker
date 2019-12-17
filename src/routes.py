# -*- encoding: utf-8

from flask import render_template

from src import app


@app.route("/")
@app.route("/index")
def index():
    return render_template(
        "reviews.html",
        name="lexie",
        reviews=[
            "This book was good.",
            "This book was also good.",
            "This book was bad.",
        ],
    )
