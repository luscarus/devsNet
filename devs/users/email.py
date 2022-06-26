from flask import render_template, current_app, url_for
from flask_babel import _
from devs.email import send_email


def send_confirm_account_email(user):
    token = user.get_token()
    confirm_url = url_for('users.confirm_account', token=token, _external=True)
    send_email(
        _('[Devs Network] - Confirmez votre compte'),
        sender=current_app.config['ADMINS'][0],
        text_body=render_template('email/account/confirm.txt',
                                  confirm_url=confirm_url, user=user),
        recipients=[user.email],
        html_body=render_template('email/account/confirm.html',
                                  confirm_url=confirm_url, user=user)
    )


def send_request_reset_email(user):
  token = user.get_token()
  reset_password_url = url_for('users.reset_password', token=token, _external=True)
  send_email(
    _('[Devs Network] - Réinitialisation de mot de passe'),
    sender=current_app.config['ADMINS'][0],
    recipients=[user.email],
    text_body=render_template('email/reset_password/request.txt', user=user, reset_password_url=reset_password_url),
    html_body=render_template('email/reset_password/request.html', user=user, reset_password_url=reset_password_url)
    )