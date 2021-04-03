"""Mesage model tests."""

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

class MessageModelTestCase(TestCase):
    """ Testing for the Message Model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User.signup("user1", "user1@email.com", "password1", None)
        uid = 1111
        u.id = uid 

        db.session.commit()

        u = User.query.get(uid)

        self.u = u
        self.id = uid

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_mesage_model(self):
        """Does basic model work?"""

        m = Message(text="Basic message text", user_id=self.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "Basic message text")

    def test_add_like(self):
        """Check a user liking a message. The like will be added to their likes"""
        m = Message(text="Basic message text", user_id=self.id)
        db.session.add(m)
        db.session.commit()

        self.u.likes.append(m)
        db.session.commit()


        self.assertEqual(len(self.u.likes), 1)
        self.assertEqual(self.u.likes[0].id, m.id)



