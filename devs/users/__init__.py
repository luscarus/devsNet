from flask import Blueprint

bp = Blueprint('users', __name__)

from devs.users import routes
