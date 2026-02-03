from flask import Blueprint

bp = Blueprint('knsb', __name__)

from .routes import *
