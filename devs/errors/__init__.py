from flask import Blueprint

bp = Blueprint('errors', __name__)

from devs.errors import routes
