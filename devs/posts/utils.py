from flask_login import current_user
from devs import db
from devs.models import Post


def create_post_for_current_user(content, language):
	post = Post(content=content, user_id=current_user.id, language=language)

	db.session.add(post)
	db.session.commit()