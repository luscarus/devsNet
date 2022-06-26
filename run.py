from devs import create_app, db, cli
from devs.models import User, Code, Post, Notification, FriendRelationship, PostLike

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Code': Code, 'Post': Post, 'FriendRelationship': FriendRelationship, 'Notification': Notification, 'PostLike': PostLike}
