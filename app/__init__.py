from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static', template_folder='templates')
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)
        db.create_all()

    return app
