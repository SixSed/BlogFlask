from flask import Flask, flash, request, redirect, url_for, render_template, g, session
import os

from .db import init_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    from . import db

    db.init_app(app)

    from . import auth, blog, change
    app.register_blueprint(auth.bp)
    app.register_blueprint(change.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app

