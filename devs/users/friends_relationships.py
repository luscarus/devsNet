from sqlalchemy import and_, or_
from devs.models import FriendRelationship


def friend_request_has_already_been_sent(user_sender, user_receiver):
    friend_relationship = FriendRelationship.query.filter(
        or_(
            and_(FriendRelationship.fk_user_sender == user_sender.id,
                 FriendRelationship.fk_user_receiver == user_receiver.id),
            and_(FriendRelationship.fk_user_sender == user_receiver.id,
                 FriendRelationship.fk_user_receiver == user_sender.id)
        )).first()

    return friend_relationship


def relation_link_to_display(user_in, other_user):

    # friend relationship
    friend_relationship = FriendRelationship.query.filter(
        or_(
            and_(FriendRelationship.fk_user_sender == user_in,
                 FriendRelationship.fk_user_receiver == other_user),
            and_(
                FriendRelationship.fk_user_sender == other_user, FriendRelationship.fk_user_receiver == user_in)
        )).first()

    if friend_relationship is None:
        # link to add the person as a friend /lien pour ajouter la personne comme ami
        return "add_relation_link"

    # if the logged in user is the one who received the friend request
    if user_in == friend_relationship.fk_user_receiver and friend_relationship.status == '0':
        # link to accept or decline the friend request /lien pour accepter ou refuser la demande d'amitié
        return "accept_reject_relation_link"

    # if the logged in user is the one who send the friend request
    elif user_in == friend_relationship.fk_user_sender and friend_relationship.status == '0':
        # link to say that the request has already been sent link to cancel the request /lien pour dire que la demande a déja été envoyée lien pour annuler la demande
        return "cancel_relation_link"

    # if the one who sent the request is logged in user or,
    # if the one who sent the request is other user
    elif (friend_relationship.fk_user_sender == user_in or friend_relationship.fk_user_sender == other_user) and friend_relationship.status == '1':
        # link to remove friendship relationship /lien pour supprimer la relation d'amitié
        return "delete_relation_link"

    else:
        # link to add the person as a friend /lien pour ajouter la personne comme ami
        return "add_relation_link"


def friends_count(user):
    friends = FriendRelationship.query.filter(
        and_(
            or_(FriendRelationship.fk_user_sender==user.id, 
                FriendRelationship.fk_user_receiver==user.id),
            FriendRelationship.status=='1')).all()
    
    return len(friends)