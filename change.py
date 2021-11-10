from flask import Blueprint
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import flash, request, redirect, url_for, render_template, g, session
import os

from flaskr2.auth import login_required
from flaskr2.db import get_db

bp = Blueprint("change", __name__, url_prefix="/change")

UPLOAD_FOLDER = 'flaskr2/static/img/'
UPLOAD_FOLDER_POST = 'flaskr2/static/img/img_post/'
UPLOAD_FOLDER_SHORT = '/static/img/'
UPLOAD_FOLDER_SHORT_POST = '/static/img/img_post/'
UPLOAD_FOLDER_AVATAR = 'flaskr2/static/img/avatar/'
UPLOAD_FOLDER_AVATAR_SHORT = '/static/img/avatar/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/<username>", methods=("GET", "POST"))
@login_required
def change(username):
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, p.created, author_id, username,p.avatar,post_image"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    if user is None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    return render_template("user_edit/change.html",
                           user=user,
                           posts=posts)


@bp.route("/delete", methods=("GET", "POST"))
@login_required
def user_delete():
    if request.method == "POST":
        username = g.user['username']
        password = request.form["password"]
        errorD = None

        db=get_db()
        user_id = session.get("user_id")

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if not check_password_hash(user["password"], password):
            errorD = "Некорректный пароль"
            flash(errorD)

        elif errorD is None:
            db.execute("DELETE FROM post WHERE author_id = ?", (user_id,))
            db.execute("DELETE FROM user WHERE id = ?", (user_id,))
            db.execute("DELETE FROM comment WHERE author_id = ?", (user_id,))
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("user_edit/user_delete.html")


@bp.route("/data_edit", methods=("GET", "POST"))
@login_required
def data_edit():
    if request.method == "POST":
        user_id = session.get("user_id")
        username = request.form["username"]
        password = request.form["password"]
        errorD = None
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if check_password_hash(user["password"], password):
            errorD = "Old password"
            flash(errorD)
        if password == '':
            password = user["password"]
        if username == '':
            username = user["username"]
        if errorD is None:
            db.execute(
                "UPDATE user SET username = ?,password = ? where id = ?", (username,generate_password_hash(password), user_id),
             )
            db.execute(
                "UPDATE comment SET username = ? where author_id = ?",
                (username, user_id),
            )
            db.commit()
            flash('Данные успешно изменены')
        return redirect(url_for("change.data_edit"))

    return render_template("user_edit/data_edit.html")


@bp.route("/avatar", methods=("GET", "POST"))
@login_required
def avatar_edit():
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.login"))
        else:
            if 'file' not in request.files:
                flash('Нет части файла')
                return redirect(url_for("change.avatar_edit", username = g.user.username))
            file = request.files['file']
            if file.filename == '':
                flash('Не выбрана фотография ')
                return redirect(url_for("change.avatar_edit", username = g.user.username))
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(UPLOAD_FOLDER_AVATAR, filename))
                fullpath = UPLOAD_FOLDER_AVATAR_SHORT + filename

                user_id = session.get("user_id")

                db = get_db()

                g.user = (
                    db.execute("UPDATE user SET avatar = ? where id = ?", (fullpath, user_id))
                )
                g.post = (
                    db.execute("UPDATE post SET avatar = ? where author_id = ?", (fullpath, user_id))
                )
                g.post = (
                    db.execute("UPDATE comment SET avatar = ? where author_id = ?", (fullpath, user_id))
                )
                db.commit()
                flash('Фотография успешно загружена')

                return redirect(url_for("change.avatar_edit"))
            else:
                flash('Доступные разрешения - png, jpg, jpeg')
                return redirect(url_for("blog.avatar_edit"))
    return render_template("user_edit/avatar_edit.html")