from flask import current_app
from flask_login import current_user
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import Length, InputRequired, EqualTo, Email, ValidationError
from devs.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Nom',
                       validators=[InputRequired(message=_l('entrer un nom')), Length(min=2, max=120)])
    pseudo = StringField('Pseudo',
                         validators=[InputRequired(message=_l('entrer un pseudo')), Length(min=3, max=20, message=_l(
                             "Pseudo trop court ou trop long! (Minimum 3 caractères) (Maximum 20 caractères)"))])
    email = StringField('Adresse Email',
                        validators=[InputRequired(message=_l('entrer une adresse email valide')),
                                    Email(message=_l('Adresse email invalide'))])
    password = PasswordField('Mot de passe',
                             validators=[InputRequired(message=_l('entrer un mot de passe')), Length(min=6, max=4096,
                                                                                                     message=_l(
                                                                                                         'Mot de '
                                                                                                         'passe trop '
                                                                                                         'court! ('
                                                                                                         'Minimum 6 '
                                                                                                         'caractères'
                                                                                                         ')'))])
    password_confirm = PasswordField('Confirmer votre mot de passe',
                                     validators=[InputRequired(message=_l('confirmer votre mot de passe')),
                                                 EqualTo('password',
                                                         message=_l('les deux mots de passe ne concordent pas'))])

    def validate_pseudo(self, pseudo):
        user = User.query.filter_by(pseudo=pseudo.data).first()
        if user:
            raise ValidationError(_l('Pseudo déja utilisé'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Adresse e-mail déja utilisée'))


class LoginForm(FlaskForm):
    username = StringField('identifiant',
                           validators=[InputRequired(message=_l('entrer votre adresse email ou votre pseudo'))])
    password = PasswordField('Mot de passe',
                             validators=[InputRequired(_l('entrer un mot de passe valide'))])

    remember_me = BooleanField('Remember me')

    def validate_username(self, username):
        user = User.query.filter((User.pseudo == username.data) | (User.email == username.data)).first()
        if not user:
            raise ValidationError((_l("Il n'y a aucun utilisateur avec cet identifiant ")))


class ProfileForm(FlaskForm):
    name = StringField('Nom',
                       validators=[InputRequired(message=_l('entrer un nom')), Length(min=2, max=120)])
    city = StringField('Ville', validators=[InputRequired(message=_l('renseigner la ville'))])
    country = StringField('Pays', validators=[InputRequired(message=_l('renseigner le pays'))])
    sex = SelectField('Sexe', choices=[('H', _l('Homme')), ('F', _l('Femme'))],
                      validators=[InputRequired(message=_l('choisissez le sexe'))])
    twitter = StringField('Twitter')
    github = StringField('Github')
    available_for_hiring = BooleanField('Disponible pour emploi?')
    bio = TextAreaField('Biographie')
    profile_img = FileField('',
                            validators=[FileAllowed(['png', 'jpg', 'gif', 'jpeg'], message=_l(
                                'Type de fichier invalide. formats supportés <png, gif, jpeg, jpg>'))])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password',
                                     validators=[InputRequired(message=_l('entrer votre mot de passe actuel')),
                                                 Length(min=6, max=4096,
                                                        message=_l('Mot de passe trop court! (Minimum 6 caractères)'))])
    new_password = PasswordField('New Password',
                                 validators=[InputRequired(message=_l('entrer le nouveau mot de passe')),
                                             Length(min=6, max=4096,
                                                    message=_l('Mot de passe trop court! (Minimum 6 caractères'))])
    new_password_confirmation = PasswordField('New Password',
                                              validators=[
                                                  InputRequired(message=_l('confirmer le nouveau mot de passe')),
                                                  EqualTo('new_password',
                                                          message=_l('les deux mots de passe ne concordent pas'))])

    def validate_current_password(self, current_password):
        if not current_user.check_password(current_password.data):
            raise ValidationError(_l("Le mot de passe actuel indiqué est incorrect"))


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                       validators=[InputRequired(message=_l('entrer une adresse email valide')),
                        Email(message=_l('Adresse email invalide'))])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(_l("Il n'y a pas de compte avec cet e-mail. Vous devez d'abord vous inscrire"))


class ResetPasswordForm(FlaskForm):
    
    password = PasswordField('Password',
                            validators=[InputRequired(message=_l('entrer un mot de passe valide')), 
                            Length(min=6, max=4096, message=_l('Mot de passe trop court! (Minimum 6 caractères)'))])
    confirmPassword = PasswordField('Confirm Password',
                                    validators=[InputRequired(message='Please confirm password'), 
                                    EqualTo('password', message=_l('les deux mots de passe ne concordent pas'))])
    
    