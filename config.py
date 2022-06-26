import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'd7dc03e9660f49c3ddf535ae'

    # DATABASE CONFIG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MAIL SERVER CONFIG, FILL THE .env FILE
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    ADMINS = ['project@devsNet.com', 'keke.projets.dev@gmail.com']

    LANGUAGES = ['fr', 'en', 'es']

    USERS_PER_PAGE = 12

    UPLOAD_FOLDER = "static/img/users/profile_pics/"
    # ALLOWED_EXTENSIONS = ['png', 'jpg', 'gif', 'jpeg']
    
    # IBM WATSON API CONFIG
    LANGUAGE_TRANSLATOR_APIKEY = os.environ.get('LANGUAGE_TRANSLATOR_APIKEY')
    LANGUAGE_TRANSLATOR_IAM_APIKEY = os.environ.get('LANGUAGE_TRANSLATOR_IAM_APIKEY')
    LANGUAGE_TRANSLATOR_URL = os.environ.get('LANGUAGE_TRANSLATOR_URL')
    LANGUAGE_TRANSLATOR_AUTH_TYPE = os.environ.get('LANGUAGE_TRANSLATOR_AUTH_TYPE')