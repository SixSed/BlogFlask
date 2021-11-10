from flask import Blueprint
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import flash, request, redirect, url_for, render_template, g, session
import os

from .auth import login_required
from .db import get_db

bp = Blueprint("blog", __name__)

UPLOAD_FOLDER = 'flaskr2/static/img/'
UPLOAD_FOLDER_POST = 'flaskr2/static/img/img_post/'
UPLOAD_FOLDER_SHORT = '/static/img/'
UPLOAD_FOLDER_SHORT_POST = '/static/img/img_post/'
UPLOAD_FOLDER_AVATAR = 'flaskr2/static/img/avatar/'
UPLOAD_FOLDER_AVATAR_SHORT = 'static/img/avatar'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, p.created, author_id, username,p.avatar,post_image"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    comments = db.execute(
        "SELECT c.id, c.body,c.created,c.post_id,c.author_id,c.avatar,c.username"
        " FROM comment c JOIN post p ON c.post_id = p.id JOIN user u ON c.username = u.username"
        " ORDER BY c.created DESC"
    ).fetchall()

    return render_template("blog/index.html", posts=posts,comments=comments)


def get_post(id, check_author=True):
    post = (
        get_db()
            .execute(
            "SELECT p.id, title, body, p.created, author_id, username,p.avatar,post_image"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
            .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")



    return post

def get_comments(id, check_author=True):
    comment = (
        get_db()
            .execute(
            "SELECT c.id, c.body,c.author_id,c.avatar,c.post_id,c.username,c.created"
            " FROM comment c JOIN post p ON c.post_id = p.id JOIN user u ON c.username = u.username"
            " WHERE c.id = ?",
            (id,),
        )
            .fetchone()
    )

    if comment is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and comment["author_id"] != g.user["id"]:
        abort(403)

    return comment


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        avatar = g.user['avatar']
        error = None

        db = get_db()
        file = None
        try:
            file = request.files['file']
        except:
            pass

        if g.user is None:
            return redirect(url_for("auth.login"))
        else:
            if not title:
                error = "Заголовок обязателен"
            if file == None:
                pass
            elif file and ((allowed_file(file.filename))==False):
                error= 'Доступные разрешения - png, jpg, jpeg'
            if error is not None:
                flash(error)
                return redirect(url_for("blog.create"))
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(UPLOAD_FOLDER_POST, filename))
                fullpath = UPLOAD_FOLDER_SHORT_POST + filename

                db.execute(
                    "INSERT INTO post (title, body, author_id, avatar, post_image) VALUES (?, ?, ?, ?, ?)",
                    (title, body, g.user["id"], avatar, fullpath),
                )
                db.commit()

                return redirect(url_for("blog.index"))
            else:
                fullpath=''
                db.execute(
                    "INSERT INTO post (title, body, author_id, avatar, post_image) VALUES (?, ?, ?, ?, ?)",
                    (title, body, g.user["id"], avatar,fullpath),
                )
                db.commit()

                return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        db = get_db()
        file = None
        try:
            file = request.files['file']
        except:
            pass

        if g.user is None:
            return redirect(url_for("auth.login"))
        else:
            if not title:
                error = "Заголовок обязателен"
            if file == None:
                pass
            elif file and ((allowed_file(file.filename)) == False):
                error = 'Доступные разрешения - png, jpg, jpeg'
            if error is not None:
                flash(error)
                return redirect(url_for("blog.create"))
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(UPLOAD_FOLDER_POST, filename))
                fullpath = UPLOAD_FOLDER_SHORT_POST + filename

                db.execute(
                    "UPDATE post SET title = ?, body = ?, post_image = ? WHERE id = ?", (title, body, fullpath, id)
                )
                db.commit()

                return redirect(url_for("blog.index"))
            else:


                fullpath = (
                   db.execute("SELECT post_image from post where id = ?", (id,)).fetchone()
                )
                db.execute(
                    "UPDATE post SET title = ?, body = ?, post_image = ? WHERE id = ?", (title, body,fullpath[0], id)
                )
                db.commit()
                return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/create_comm", methods=("GET", "POST"))
@login_required
def create_comm(id):
    post = get_post(id)
    if request.method == "POST":
        db=get_db()
        body = request.form["body"]
        avatar = g.user['avatar']
        db.execute(
            "INSERT INTO comment (post_id,author_id, body, avatar,username) VALUES (?, ?, ?, ?, ?)",
            (post[0],g.user["id"], body, avatar, g.user['username']),
        )
        db.commit()
        return redirect(url_for("blog.index"))
    return render_template("comment/create_comm.html")


@bp.route("/<int:id>/update_comm", methods=("GET", "POST"))
@login_required
def update_comm(id):
    comment = get_comments(id)
    if request.method == "POST":
        body = request.form["body"]
        error = None

        db = get_db()

        if g.user is None:
            return redirect(url_for("auth.login"))
        else:
            if not body:
                error = "Сообщение обязательно"
            if error is not None:
                flash(error)
                return redirect(url_for("blog.create"))
            else:
                db.execute(
                    "UPDATE comment SET body = ? WHERE id = ?", (body, id)
                )
                db.commit()

                return redirect(url_for("blog.index"))


    return render_template("comment/update_comm.html", comment=comment)


@bp.route("/<int:id>/delete_comm", methods=("POST",))
@login_required
def delete_comm(id):
    get_comments(id)
    db = get_db()
    db.execute("DELETE FROM comment WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))



@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))







