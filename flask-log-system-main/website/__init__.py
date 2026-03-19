from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from logging.config import dictConfig
from .log_json import log_event
import logging
import time
import uuid
import os

db = SQLAlchemy()
DB_NAME = "database.db"

dictConfig({
    "version": 1,
    "formatters": {
        "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"},
        "json_only": {"format": "%(message)s"},
    },
    "handlers": {
        "console": {  
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default"
        },
        "json_console": {  
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json_only"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "instance/app.log"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
})

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # ✅ request-logg för varje request (perfekt för Grafana)
    @app.before_request
    def _start_timer():
        g.start = time.time()
        g.request_id = uuid.uuid4().hex

    @app.after_request
    def _log_request(response):
        duration_ms = int((time.time() - g.start) * 1000)

        log_event(
            logging.INFO,
            "request",
            request_id=getattr(g, "request_id", None),
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


