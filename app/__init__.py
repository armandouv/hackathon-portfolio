import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# from data.load_data import load_projects, load_profiles
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)

load_dotenv()

# def create_app():
app = Flask(__name__)
app.config["SECRET_KEY"] = "t4{pt_+FS3T#G\Gfs/F"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sql"
"""app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)"""

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    def repr(self):
        return "<User %r>" % self.username


# default=DateTime.now()
class PostModel(UserMixin, db.Model):
    __tablename__ = "post"
    id_post = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    title = db.Column(db.String(40), nullable=False)
    text = db.Column(db.String(180), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    last_modificacion = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.ForeignKey("users.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return UserModel.query.get(int(user_id))


"""
base_url = os.getenv("URL")
projects_base_url = base_url + "/projects/"
profiles_base_url = base_url + "/profiles/"

projects = load_projects()
profiles = load_profiles()"""


@app.route("/")
def index():
    return render_template("index.html", title="Team Kenargi's portfolio")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.name)


"""
@app.route("/projects/<name>")
def get_project(name):
    if name not in projects:
        return abort(404)
    return render_template(
        "project.html", item=projects[name], title=name, url=projects_base_url + name
    )


@app.route("/profiles/<name>")
def get_profile(name):
    if name not in profiles:
        return abort(404)
    title = name + "'s Profile"
    return render_template(
        "profile.html", item=profiles[name], title=title, url=profiles_base_url + name
    )"""


@app.route("/health")
def get_health():
    return "", 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page not found"), 404


@app.route("/addpost", methods=("GET", "POST"))
def addpost():
    if session["username"] in session:
        return render_template("index.html", title="Home")
    else:
        return render_template("login.html", title="Login")


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
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
            return redirect(url_for("auth.login"))

        if error is None:
            new_user = UserModel(
                firstname,
                lastname,
                username,
                generate_password_hash(password, method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            return error, 418

    return redirect(url_for("auth.login"))
    # return render_template("register.html", title="Sign up")


@app.route("/login", methods=("GET", "POST"))
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


@app.route("/logout")
@login_required
def logout():
    # remove the username from the session if it's there
    logout_user()
    return redirect(url_for("main.index"))
