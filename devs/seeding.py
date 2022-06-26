from faker import Faker
from devs import db
from devs.models import User, FriendRelationship


faker = Faker()


def generate_fake_users():
    for _ in range(50):
        fake_user = User(
            name=faker.unique.name(),
            pseudo=faker.profile()['username'],
            has_been_confirmed=faker.boolean(),
            email=faker.unique.email(),
            city=faker.city(),
            country=faker.country(),
            bio=faker.sentence(),
            sex=faker.random.choice(['H', 'F']),
            created_at=faker.date_time_this_year(),
            available_for_hiring=faker.boolean())
        fake_user.set_password('12345678@')
        friend_relationship = FriendRelationship(sender=fake_user, receiver=fake_user, status='2')
        db.session.add(fake_user)
        db.session.add(friend_relationship)
    db.session.commit()
    return "50 fake users added"
