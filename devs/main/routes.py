from flask import Blueprint, render_template, g, request
from flask_babel import get_locale

from devs.main import bp


@bp.before_app_request
def before_request():
    g.locale = str(get_locale())

# Show the Homepage
@bp.route('/')
def homepage():
    return render_template('main/index.html', title='Accueil')
