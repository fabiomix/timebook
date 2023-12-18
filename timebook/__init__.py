from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

babel = Babel()
csrf = CSRFProtect()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "supersecretkey"

    # app.config.from_pyfile(config_filename)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///time.db"
    app.config["BABEL_DEFAULT_LOCALE"] = "it"

    # extensions init
    babel.init_app(app)
    csrf.init_app(app)
    db.init_app(app)

    # blueprints register
    from timebook.blueprints.web import web_app
    app.register_blueprint(web_app)
    from timebook.blueprints.cli import cli_app
    app.register_blueprint(cli_app)

    # register the template filter into Jinja
    from timebook.utils import format_timedelta
    app.jinja_env.filters["format_timedelta"] = format_timedelta

    # create the table schema in the database
    with app.app_context():
        db.create_all()

    return app
