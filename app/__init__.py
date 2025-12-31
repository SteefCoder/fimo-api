from flask import Flask

from config import Config

from app.routes import create_hello_view

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    create_hello_view(app)

    return app
