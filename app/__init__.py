from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
load_dotenv()
app = Flask(__name__)


def create_app():
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

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import UserModel

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return UserModel.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app


migrate = Migrate(app, db)


@app.route("/")
def index():
    return render_template("index.html", title="Team Kenargi's portfolio")
