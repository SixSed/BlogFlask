import functools

from flask import Blueprint, flash, g, request, redirect, render_template, session, url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from .db import get_db

UPLOAD_FOLDER = '/static/img/avatar/'
bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        avatar = UPLOAD_FOLDER + "non.png"
        db = get_db()
        error = None

        if not username:
            error = "Требуется имя пользователя"
        elif not password:
            error = "Требуется пароль"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, avatar) VALUES (?, ?,?)",
                    (username, generate_password_hash(password), avatar),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Пользователь {username} уже зарегистрирован"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Некорректное имя пользователя"
        elif not check_password_hash(user["password"], password):
            error = "Некорректный пароль"

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
