from langdetect import detect, LangDetectException
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_babel import _
from flask_login import login_user, logout_user, current_user, login_required, fresh_login_required
from devs import db
from devs.posts.forms import PostForm
from devs.posts.utils import create_post_for_current_user
from devs.users import bp
from devs.users.forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm, RequestResetForm, \
    ResetPasswordForm
from devs.models import User, Post, FriendRelationship, Notification, PostLike
from devs.users.email import send_confirm_account_email, send_request_reset_email
from devs.users.utils import save_image
from devs.users.friends_relationships import friend_request_has_already_been_sent, relation_link_to_display


def get_user(user_id):
    user = User.query.get(user_id)
    return user


# Registering a new user
@bp.route('/auth/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # create and add user to database
        user = User(
            name=form.name.data,
            pseudo=form.pseudo.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)

        friend_relationship = FriendRelationship(sender=user, receiver=user, status='2')

        db.session.add(user)
        db.session.add(friend_relationship)
        db.session.commit()

        flash(_("Merci d'avoir crée un compte!, vous pouvez maintenant vous connecter"), "info")
        return redirect(url_for('users.login'))

    return render_template('users/register.html', title='Inscription', form=form)


@bp.route('/confirm-account-email/')
@login_required
def confirm_account_email():
    if current_user.is_authenticated:
        if current_user.has_been_confirmed is False:
            send_confirm_account_email(current_user)
            flash(_('Un e-mail a été envoyé avec des instructions pour confirmer votre compte'), 'success')
            return redirect(url_for('users.profile', id=current_user.id))

        flash(_('Votre adresse e-mail a déja été confirmée'), 'info')
        return redirect(url_for('users.profile', id=current_user.id))

    flash(_("S'il vous plait, connectez-vous pour confirmer votre compte"), 'warning')
    return redirect(url_for('users.login'))


@bp.route('/confirm-account/<token>/')
def confirm_account(token):
    user = User.verify_token(token)
    if not user:
        flash(_('Le lien a expiré'), 'warning')
        return redirect(url_for('main.homepage'))

    user.has_been_confirmed = True
    db.session.commit()
    flash(_("Merci d'avoir confirmé votre adresse e-mail"), 'success')
    return redirect(url_for('users.profile', id=current_user.id))


# Login to the app
@bp.route('/auth/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))

    form = LoginForm()
    if form.validate_on_submit():
        foundedUser = User.query.filter(
            (User.pseudo == form.username.data) | (User.email == form.username.data)).first()
        if foundedUser is None or not foundedUser.check_password(form.password.data):
            flash(_("Utilisateur inconnu ou mauvais mot de passe"), "danger")
            return render_template('users/login.html', title='Connexion', form=form)

        login_user(foundedUser, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.homepage')
        return redirect(next_page)

    return render_template('users/login.html', title='Connexion', form=form)


@bp.route('/auth/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@bp.route('/profile/<int:id>/', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = get_user(id)
    if not user:
        return redirect(url_for('main.homepage'))

    posts = Post.query \
        .filter_by(user_id=user.id).all()

    friends = []

    # get all user's friends 
    for friendship in user.friends():
        if friendship.sender != user:
            friends.append(friendship.sender)

    for friendship in user.friends():
        if friendship.receiver != user:
            friends.append(friendship.receiver)

    # add user's friends posts to posts
    for friend in friends:
        friend_posts = Post.query.filter_by(author=friend).all()
        if friend_posts:
            posts.extend(friend_posts)

        posts = sorted(posts, key=lambda x: x.created_at, reverse=True)

    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.content.data)
        except LangDetectException:
            language = ''
        create_post_for_current_user(form.content.data, language)
        flash(_('Votre publication est maintenant en ligne !'), 'success')
        return redirect(url_for('users.profile', id=current_user.id))

    return render_template('users/user_profile.html',
                           form=form,
                           user=user,
                           posts=posts,
                           tilte='Mon Profil',
                           relation_link_to_display=relation_link_to_display
                           )


@bp.route('/edit/profile/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    user = get_user(id)
    if not user:
        return redirect(url_for('main.index'))

    if user == current_user:
        form = ProfileForm(obj=current_user)
        filename = current_user.profile_img

        if form.validate_on_submit():
            if request.files.get('profile_img'):
                img_file = save_image(current_user, request.files.get('profile_img'))
            else:
                img_file = filename
            """for key, data in dict(request.form).items():
                if key in vars(user).keys():
                    user.key = data
                    print(f'{key}: {user.key}')
            """
            user.name = form.name.data
            user.city = form.city.data
            user.profile_img = img_file
            user.country = form.country.data
            user.sex = form.sex.data
            user.twitter = form.twitter.data
            user.github = form.github.data
            if form.available_for_hiring.data is True:
                user.available_for_hiring = True
            else:
                user.available_for_hiring = False
            user.bio = form.bio.data
            db.session.commit()
            flash(_("Votre profil a ete mis a jour"), 'info')
            return redirect(url_for('users.profile', id=current_user.id))

        return render_template('users/edit_profile.html', title='Modifier mon profil', form=form, user=user)

    return redirect(url_for('users.profile', id=user.id))


@bp.route('/list/users/')
def list_users():
    page = request.args.get('page', 1, type=int)

    page_users = User.query \
        .filter_by(is_active=True) \
        .order_by(User.pseudo.asc()) \
        .paginate(page=page, per_page=current_app.config['USERS_PER_PAGE'])

    return render_template('users/list_users.html', title='Liste des utilisateurs', page_users=page_users)


# Change user password
@bp.route('/change-password/<int:id>/', methods=['GET', 'POST'])
@login_required
def change_password(id):
    user = get_user(id)

    if user == current_user:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            user.set_password(form.new_password.data)
            db.session.commit()
            flash(_('Félicitations, votre mot de passe a été mis à jour'), 'success')
            return redirect(url_for('users.profile', id=current_user.id))
        return render_template('users/change_password.html', title='Changer mon mot de passe', form=form)

    return redirect(url_for('users.profile', id=user.id))


# Change user password
@bp.route('/add-friend/<int:id>/')
@login_required
def add_friend(id):
    user = get_user(id)

    if user != current_user:
        if friend_request_has_already_been_sent(current_user, user):
            flash(_("Cet utilisateur vous a deja envoyé une demande d'amitié"), "info")
            return redirect(url_for('users.profile', id=user.id))
        friend_relationship = FriendRelationship(sender=current_user, receiver=user)
        friend_request_sent_notif = Notification(name='friend_request_sent', subject_id=user.id,
                                                 user_id=current_user.id)
        db.session.add(friend_relationship)
        db.session.add(friend_request_sent_notif)
        db.session.commit()
        flash(_("Votre demande d'amitié a été envoyée avec success"), "success")
        return redirect(url_for('users.profile', id=user.id))

    return redirect(url_for('users.profile', id=current_user.id))


# cancel a friend relationship request
@bp.route('/delete-friend/<int:id>/')
@login_required
def delete_friend(id):
    user = get_user(id)

    if user != current_user:
        if not friend_request_has_already_been_sent(current_user, user):
            return redirect(url_for('users.profile', id=user.id))
        friend_relationship = friend_request_has_already_been_sent(current_user, user)
        db.session.delete(friend_relationship)
        db.session.commit()
        flash(_("Vous n'êtes plus ami avec cet utilisateur"), "warning")
    return redirect(url_for('users.profile', id=user.id))


# accept a friend relationship request
@bp.route('/accept-friend/<int:id>/')
@login_required
def accept_friend_request(id):
    user = get_user(id)

    if user != current_user:
        if not friend_request_has_already_been_sent(current_user, user):
            return redirect(url_for('users.profile', id=user.id))
        friend_relationship = friend_request_has_already_been_sent(current_user, user)
        friend_relationship.status = '1'
        friend_request_accepted_notif = Notification(name='friend_request_accepted', subject_id=user.id,
                                                     user_id=current_user.id)
        db.session.add(friend_request_accepted_notif)
        db.session.commit()
        flash(_("Vous êtes à présent ami avec cet utilisateur"), "primary")

    return redirect(url_for('users.profile', id=user.id))


@bp.route('/notifications/')
@login_required
def notifs():
    # Nous récupérons toutes les notifications de l'utilisateur connecté
    # (Aussi bien les notifications lues que les notifications non lues).
    notifications = Notification.query.filter_by(subject_id=current_user.id).order_by(
        Notification.created_at.desc()).all()

    # Après avoir récupéré les notifications de l'utilisateur connecté,
    # nous modifions la valeur de leur attribut 'seen' afin d'indiquer que
    # l'utilisateur vient de lire ces notifications.
    for notif in notifications:
        notif.seen = '1'
    db.session.commit()

    return render_template('users/notifications.html', title='Notifications', notifications=notifications)


@bp.route('/delete-post/<int:id>/')
@login_required
def delete_post(id):
    post = Post.query.get(id)

    if post.author == current_user:
        db.session.delete(post)
        db.session.commit()
        flash(_('la publication a été supprimée'), 'warning')
        return redirect(url_for('users.profile', id=post.author.id))

    return redirect(url_for('users.profile', id=current_id))


@bp.route('/like-post/<int:id>/')
@login_required
def like_post(id):
    post = Post.query.get(id)
    liked_post = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if not liked_post:
        db.session.add(PostLike(user_id=current_user.id, post_id=post.id))
        db.session.commit()

    return jsonify({'result': 'liked post ' + str(post.id)})


@bp.route('/unlike-post/<int:id>/')
@login_required
def unlike_post(id):
    post = Post.query.get(id)
    liked_post = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if liked_post:
        db.session.delete(liked_post)
        db.session.commit()

    return jsonify({'result': 'unliked post ' + str(post.id)})


@bp.route('/reset-request-password/', methods=['GET', 'POST'])
def reset_request_password():
    if current_user.is_authenticated:
        return redirect(url_for('users.profile', id=current_user.id))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_request_reset_email(user)
        flash(_('Un e-mail a été envoyé avec des instructions pour réinitialiser votre mot de passe'), 'success')

        return redirect(url_for('users.login'))

    return render_template('users/reset_request_password.html', form=form,
                           title='Demande de réinitialisation du mot de passe')


@bp.route('/reset-password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.profile', id=current_user.id))

    user = User.verify_token(token)
    if not user:
        flash(_('Votre jeton est invalide ou a expiré'), 'warning')
        return redirect(url_for('users.reset_request_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Votre mot de passe a été mis à jour!'), 'success')

        return redirect(url_for('users.login'))

    return render_template('users/reset_password.html', form=form, title='Réinitialisation du mot de passe')
