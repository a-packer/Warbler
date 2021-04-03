"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u1 = User.signup("user1", "user1@email.com", "password1", None)
        u1_id = 1111
        u1.id = u1_id 

        u2 = User.signup("user2", "user2@email.com", "password2", None)
        u2_id = 2222
        u2.id = u2_id 

        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.u1_id = u1_id

        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        self.assertEqual(str(u), f'<User #{u.id}: {u.username}, {u.email}>')

    # FOLLOWING TESTS

    def test_users_following(self):
        # user1 starts following user2
        # test user1 following and user2 followers
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.followers), 1)

        self.assertEqual(self.u1.following[0].id, self.u2_id)
        self.assertEqual(self.u2.followers[0].id, self.u1_id)

    def test_is_followed_by(self):
        # user1 starts following user2
        self.u1.following.append(self.u2)
        db.session.commit()

        # test is_followed_by for user 2
        self.assertEqual(self.u2.is_followed_by(self.u1), 1)

    def test_is_following(self):
        # user1 starts following user2
        self.u1.following.append(self.u2)
        db.session.commit()

        # test is_following for user 1
        self.assertEqual(self.u1.is_following(self.u2), 1)


    # SIGN UP / SIGN IN TESTS

    def test_valid_signup(self):
        u_test = User.signup("signinusertest", "signintest@email.com", "password3", None)
        uid = 3333
        u_test.id = uid
        db.session.commit()

        user_test = User.query.get_or_404(uid)

        self.assertEqual(user_test.username, "signinusertest")
        self.assertEqual(user_test.email, "signintest@email.com")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 4444
        invalid.id = uid
        # if data missing, Integrity Error will appear after db.session.commit()
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_valid_sign_in(self):
        u = User.authenticate(self.u1.username, "password1")
        self.assertIsNotNone(u)

    def test_invalid_password(self):
        u = User.authenticate(self.u1.username, "badpassword")
        self.assertFalse(u)

    def test_invalid_password(self):
        u = User.authenticate("wrong username", "password1")
        self.assertFalse(u)
    









        