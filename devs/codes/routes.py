from flask import render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from flask_babel import get_locale

from devs import db
from devs.models import Code
from devs.codes import bp
from devs.codes.forms import CodeForm

from devs.posts.utils import create_post_for_current_user

from flask_babel import _


def get_code(code_id):
    code = Code.query.get(code_id)
    return code


@bp.route('/share/code/', methods=['GET', 'POST'])
@login_required
def share_code():
    form = CodeForm()
    if form.validate_on_submit():
        code = Code(code=form.code.data, user_id=current_user.id)
        db.session.add(code)
        db.session.commit()

        full_url = "localhost:5000" + url_for('codes.show_code', id=code.id)
        create_post_for_current_user(f"{_('Je viens de publier un nouveau code source:')} {full_url}",
                                        str(get_locale()))

        flash(_("Code source enregistré"), "success")
        return redirect(url_for('codes.show_code', id=code.id))
    return render_template('codes/share_code.html', title='Partage de code source', form=form)


@bp.route('/show/code/<int:id>/')
@login_required
def show_code(id):
    code = get_code(id)
    if not code:
        return redirect(url_for('codes.share_code'))
    return render_template('codes/show_code.html', title='Affichage code source', code=code)


@bp.route('/clone/code/<int:id>/', methods=['GET', 'POST'])
@login_required
def clone(id):
    code = get_code(id)
    if not code:
        return redirect(url_for('codes.share_code'))
    form = CodeForm(obj=code)
    return render_template('codes/share_code.html', title='Partage de code source', form=form)
