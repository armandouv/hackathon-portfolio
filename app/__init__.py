import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort, request, redirect, flash
from flask_login import (
    LoginManager,
    UserMixin, login_user, login_required, logout_user, current_user,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from werkzeug.security import generate_password_hash, check_password_hash

from data.load_data import load_posts_info

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, engine_options={'connect_args': {'connect_timeout': 10}})
migrate = Migrate(app, db)


class UserModel(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(1000), unique=True)
    firstname = db.Column(db.String(1000))
    lastname = db.Column(db.String(1000))
    password = db.Column(db.String(1000))

    def __init__(self, email, password, firstname, lastname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self):
        return f"<User {self.username}>"


class PostModel(db.Model):
    __tablename__ = "post"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    title = db.Column(db.String(1000))
    text = db.Column(db.String(1000))
    creation_date = db.Column(DateTime(timezone=True), server_default=func.now())
    modification_date = db.Column(DateTime(timezone=True), onupdate=func.now())
    created_by = db.Column(db.ForeignKey("user.id"))

    def __init__(self, title, text, created_by):
        self.title = title
        self.text = text
        self.created_by = created_by

    def __repr__(self):
        return f"<Post {self.title}>"


db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "app.login"
login_manager.init_app(app)

base_url = os.getenv("URL")
posts_base_url = base_url + "/posts/"


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return UserModel.query.get(int(user_id))


# TODO: This will be deleted since posts will be stored in the database
posts_info = load_posts_info()


@app.route("/")
def index():
    # TODO: Implement pagination
    return render_template(
        "index.html",
        # TODO: query posts info page from db
        posts=posts_info,
        title="Blog",
        url=base_url,
    )


@app.route("/posts/<post_id>")
def get_post(post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post is None:
        return abort(404)
    return render_template(
        "post.html", post=post, title=post.title, url=posts_base_url + post_id
    )


@app.route("/posts/<post_id>/edit")
def get_edit_post(post_id):
    # TODO: query post from db
    if post_id not in posts_info:
        return abort(404)
    title = posts_info[post_id]["title"]
    return render_template(
        "edit_post.html", item=posts_info[post_id], title=title, url=posts_base_url + post_id + "/edit"
    )


@app.route("/posts/new")
def get_create_post():
    if current_user.is_authenticated:
        return render_template(
            "create_post.html", title="Create new post", url=posts_base_url + "new"
        )
    else:
        return render_template("login.html", title="Login")


# TODO: Implement edit post endpoint

@app.route("/posts", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title")
    text = request.form.get("text")
    new_post = PostModel(title, text, current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return redirect("https://localhost/posts/" + str(new_post.id))


@app.route("/health")
def get_health():
    return "", 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page not found"), 404


@app.route("/signup", methods=("GET", "POST"))
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        error = None

        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif not firstname:
            error = "First name is required."
        elif not lastname:
            error = "Last name is required."
        elif UserModel.query.filter_by(email=email).first() is not None:
            error = f"User {email} is already registered."

        if error is None:
            new_user = UserModel(email, generate_password_hash(password), firstname, lastname)
            db.session.add(new_user)
            db.session.commit()
            return redirect("https://localhost/login")
        else:
            flash(error)
            return redirect("https://localhost/signup")

    if current_user.is_authenticated:
        return redirect("https://localhost")
    return render_template("signup.html", title="Sign up")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        error = None
        remember = True if request.form.get("remember") else False
        user = UserModel.query.filter_by(email=email).first()

        if user is None:
            error = "Incorrect email."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            login_user(user, remember=remember)
            return redirect("https://localhost")
        else:
            flash("Please check your login details and try again.")
            return redirect("https://localhost/login")

    if current_user.is_authenticated:
        return redirect("https://localhost")
    return render_template("login.html", title="Login")


@app.route("/logout")
@login_required
def logout():
    # remove the username from the session if it's there
    logout_user()
    return redirect("https://localhost")
