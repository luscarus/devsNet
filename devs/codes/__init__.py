from flask import Blueprint

bp = Blueprint('codes', __name__)

from devs.codes import routes
