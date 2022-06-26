from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class CodeForm(FlaskForm):
    code = TextAreaField('Code',
                         validators=[InputRequired(message=_l('ecrivez du code'))])
