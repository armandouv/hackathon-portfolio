from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required
from .models import UserModel

auth = Blueprint("auth", __name__)


@auth.route("/addpost", methods=("GET", "POST"))
def addpost():
    if session["username"] in session:
        return render_template("index.html", title="Home")
    else:
        return render_template("login.html", title="Login")


@auth.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        else:
            user = UserModel.query.filter_by(username=username).first()

        if user:
            flash("Email address already exists")
            return redirect(url_for("auth.signup"))

        if error is None:
            new_user = UserModel(
                username, generate_password_hash(password, method="sha256")
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            return error, 418

    return redirect(url_for("auth.login"))
    # return render_template("register.html", title="Sign up")


@auth.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        remember = True if request.form.get("remember") else False
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            login_user(user, remember=remember)
            return redirect(url_for("main.index"))
        else:
            flash("Please check your login details and try again.")
            return redirect(url_for("auth.login"))

    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    # remove the username from the session if it's there
    logout_user()
    return redirect(url_for("main.index"))
