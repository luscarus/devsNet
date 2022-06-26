from datetime import datetime
from hashlib import md5
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import and_, or_

from devs import db, bcrypt, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class FriendRelationship(db.Model):
    __tablename__ = 'friend'

    fk_user_sender = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    fk_user_receiver = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.Enum('0', '1', '2', name='status'), nullable=False, default='0')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    pseudo = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    has_been_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    city = db.Column(db.String(255))
    profile_img = db.Column(db.String(255))
    country = db.Column(db.String(255))
    sex = db.Column(db.String(1))
    twitter = db.Column(db.String(255))
    github = db.Column(db.String(255))
    available_for_hiring = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text)
    codes = db.relationship('Code', backref='owner', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    user_sender = db.relationship('FriendRelationship', backref='sender', primaryjoin=id == FriendRelationship.fk_user_sender)
    user_receiver = db.relationship('FriendRelationship', backref='receiver', primaryjoin=id == FriendRelationship.fk_user_receiver)

    def __repr__(self):
        return f"user: '{self.pseudo}'"

    def set_avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=600):
        return jwt.encode(
            {'getting_token': self.id,
             'exp': time() + expires_in,
             },
            current_app.config['SECRET_KEY'], algorithm='HS256')

    def friends(self):
        user_friends = FriendRelationship.query.filter(
                    and_(
                        or_(FriendRelationship.fk_user_sender==self.id, 
                                FriendRelationship.fk_user_receiver==self.id),
                        FriendRelationship.status=='1')).all()
        return user_friends

    def get_unread_notifs(self):
        return Notification.query.filter_by(subject_id=self.id, seen='0').all()

    def has_already_liked_post(self, post):
        return PostLike.query.filter_by(user_id=self.id, post_id=post).first()

    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['getting_token']
        except:
            return
        return User.query.get(id)


class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"code: '{self.code}'"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(5))

    def get_likes_count(self):
        return len(PostLike.query.with_entities(PostLike.user_id).filter_by(post_id=self.id).all())

    def get_likers(self):
        likers = db.session.query(User, PostLike) \
                    .add_columns(User.id, User.pseudo) \
                    .join(PostLike, PostLike.user_id == User.id) \
                    .filter(PostLike.post_id == self.id) \
                    .order_by(PostLike.id.desc()) \
                    .limit(3).all()
        return likers

    def __repr__(self):
        return f"post: '{self.content}'"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seen = db.Column(db.Enum('0', '1', name='seen'), nullable=False, default='0')
    user = db.relationship("User")


class PostLike(db.Model):
    __tablename__ = 'post_like'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
