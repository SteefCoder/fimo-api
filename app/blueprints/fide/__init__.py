from flask import Blueprint

bp = Blueprint('fide', __name__)

from .routes import *
