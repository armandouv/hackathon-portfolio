import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort, request
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import get_db
from data.load_data import load_projects, load_profiles
from . import db

load_dotenv()
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
db.init_app(app)

base_url = os.getenv("URL")
projects_base_url = base_url + "/projects/"
profiles_base_url = base_url + "/profiles/"

projects = load_projects()
profiles = load_profiles()


@app.route('/')
def index():
    return render_template('index.html', profiles=profiles, projects=projects, title="Team Kenargi's portfolio",
                           url=base_url)


@app.route('/projects/<name>')
def get_project(name):
    if name not in projects:
        return abort(404)
    return render_template('project.html', item=projects[name], title=name, url=projects_base_url + name)


@app.route('/profiles/<name>')
def get_profile(name):
    if name not in profiles:
        return abort(404)
    title = name + "'s Profile"
    return render_template('profile.html', item=profiles[name], title=title, url=profiles_base_url + name)


@app.route('/health')
def get_health():
    return '', 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Page not found"), 404


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    return render_template("register.html", title="Sign up")


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    return render_template("login.html", title="Login")
