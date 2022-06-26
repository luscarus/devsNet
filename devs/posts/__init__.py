from flask import Blueprint

bp = Blueprint('posts', __name__)

from devs.posts import routes
