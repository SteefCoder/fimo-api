from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    from app.routes import create_hello_view
    create_hello_view(app)

    from app.knsb import bp as knsb_bp
    app.register_blueprint(knsb_bp, url_prefix='/knsb')

    from app.fide import bp as fide_bp
    app.register_blueprint(fide_bp, url_prefix='/fide')

    from app.models import db
    db.init_app(app)

    return app
