from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length


class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[InputRequired(message=_l('écriver quelque chose')),
                                                   Length(min=3, max=140, message=_l
                                                   ("trop court ou trop long! (Minimum 3 caractères) (Maximum 140 "
                                                    "caractères)"))])
