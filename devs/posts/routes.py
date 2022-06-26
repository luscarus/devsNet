from flask import Blueprint, jsonify, request
from flask_login import login_required

from devs.translate import translate
from devs.posts import bp


@bp.route('/translate/post/', methods=['POST'])
@login_required
def translate_text():
	return jsonify({'text': translate(request.form['text'],
	                                  request.form['source_language'],
	                                  request.form['dest_language'])})
    
