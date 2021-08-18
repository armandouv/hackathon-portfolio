import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort, request, redirect, flash, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
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

db = SQLAlchemy(app, engine_options={"connect_args": {"connect_timeout": 10}})
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
    modification_date = db.Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = db.Column(db.ForeignKey("user.id"))

    def __init__(self, title, text, created_by):
        self.title = title
        self.text = text
        self.created_by = created_by

    def __repr__(self):
        return f"<Post {self.title}>"


# Configuration for flask_mail
# This setup is specifically for gmail,
# other email servers have different configuration settings
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
# These need to be setup in .env file
app.config["MAIL_USERNAME"] = os.getenv("EMAIL")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")

# Emails are managed through a mail instance
mail = Mail(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "app.login"
login_manager.init_app(app)

base_url = os.getenv("URL")
posts_base_url = base_url + "/posts/"


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table,
    # use it in the query for the user
    return UserModel.query.get(int(user_id))


@app.route("/")
def index():
    page = request.args.get("page")

    if page and not page.isdigit():
        return abort(404)

    page = 1 if page is None else page

    page = int(page)
    posts_query = PostModel.query.order_by(PostModel.id.desc()).paginate(
        page, 12, False
    )

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Compose email and send
        msg = Message(
            subject=f"Mail from {name}",
            body=f"Name: {name}\nEmail: {email}\n\nMessage: {message}",
            recipients=[os.getenv("EMAIL")],
            sender=os.getenv("EMAIL"),
        )
        mail.send(msg)
        return render_template(
            "index.html",
            posts=posts_query.items,
            title="Blog",
            url=base_url,
            current_page=page,
            has_previous_page=posts_query.has_prev,
            has_next_page=posts_query.has_next,
        )

    return render_template(
        "index.html",
        posts=posts_query.items,
        title="Blog",
        url=base_url,
        current_page=page,
        has_previous_page=posts_query.has_prev,
        has_next_page=posts_query.has_next,
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
@login_required
def get_edit_post(post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post is None:
        return abort(404)
    if post.created_by != current_user.id:
        return abort(403)

    return render_template(
        "edit_post.html",
        post=post,
        title=post.title,
        url=posts_base_url + post_id + "/edit",
    )


@app.route("/posts/new")
def get_create_post():
    if current_user.is_authenticated:
        return render_template(
            "create_post.html", title="Create new post", url=posts_base_url + "new"
        )
    else:
        return render_template("login.html", title="Login")


@app.route("/posts", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title")
    text = request.form.get("text")
    new_post = PostModel(title, text, current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for("get_post", post_id=str(new_post.id)))


@app.route("/posts/<post_id>", methods=["POST"])
@login_required
def edit_post(post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post is None:
        return abort(404)
    if post.created_by != current_user.id:
        return abort(403)

    new_title = request.form.get("title")
    new_text = request.form.get("text")

    post.title = new_title
    post.text = new_text
    db.session.commit()

    return redirect(url_for("get_post", post_id=str(post.id)))


@app.route("/posts/<post_id>/delete")
@login_required
def delete_post(post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post is None:
        return abort(404)
    if post.created_by != current_user.id:
        return abort(403)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("index"))


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
            new_user = UserModel(
                email, generate_password_hash(password), firstname, lastname
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            flash(error)
            return redirect(url_for("signup"))

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("register_new.html", title="Sign up")


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
            return redirect(url_for("index"))
        else:
            flash("Please check your login details and try again.")
            return redirect(url_for("login"))

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("login_new.html", title="Login")


@app.route("/logout")
@login_required
def logout():
    # remove the username from the session if it's there
    logout_user()
    return redirect(url_for("index"))
