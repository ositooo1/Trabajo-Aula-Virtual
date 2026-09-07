from flask import (
    Blueprint,
    render_template
)


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def homepage():

    return render_template(
        "homepage.html"
    )


@main_bp.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


@main_bp.route("/students")
def students_page():

    return render_template(
        "students.html"
    )


@main_bp.route("/content")
def content_page():

    return render_template(
        "content.html"
    )


@main_bp.route("/evaluations")
def evaluations_page():

    return render_template(
        "evaluations.html"
    )