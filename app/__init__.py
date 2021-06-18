import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort

from data.load_data import load_projects, load_profiles

load_dotenv()
app = Flask(__name__)

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
