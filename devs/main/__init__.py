from flask import Blueprint

bp = Blueprint('main', __name__)

from devs.main import routes
