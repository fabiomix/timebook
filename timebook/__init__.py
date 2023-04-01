from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy

babel = Babel()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # app.config.from_pyfile(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///time.db'
    app.config['BABEL_DEFAULT_LOCALE'] = 'it'

    # Babel init
    babel.init_app(app)

    # SQLAlchemy init
    db.init_app(app)

    # blueprints register
    from timebook.blueprints.timesheet import timesheet_app
    app.register_blueprint(timesheet_app)

    # create the table schema in the database
    with app.app_context():
        db.create_all()

    return app
