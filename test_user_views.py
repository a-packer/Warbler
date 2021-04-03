"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="pw_testuser1",
                                    image_url=None)
        self.testuser1_id = 1111
        self.testuser1.id = self.testuser1_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="pw_testuser2",
                                    image_url=None)
        self.testuser2_id = 1112
        self.testuser2.id = self.testuser2_id
        
        self.testuser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="pw_testuser3",
                                    image_url=None) 
        self.testuser3_id = 1113  
        self.testuser3.id = self.testuser3_id                              


        db.session.add_all([self.testuser1, self.testuser2, self.testuser3])                           
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_list_users(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1", str(resp.data))
            self.assertIn("testuser2", str(resp.data))
            self.assertIn("testuser3", str(resp.data))


    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1_id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser1", str(resp.data))


    def test_users_show_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id
            following = Follows(user_being_followed_id=self.testuser2_id, user_following_id=self.testuser1_id)
            db.session.add(following)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser1_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser2", str(resp.data))

    def test_show_followers(self):
        following = Follows(user_being_followed_id=self.testuser3_id, user_following_id=self.testuser1_id)
        db.session.add(following)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser3_id

            resp = c.get(f"/users/{self.testuser3_id}/followers")

            self.assertIn("@testuser1", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))

    
    def test_unauthorized_following_view(self):
        following = Follows(user_being_followed_id=self.testuser3_id, user_following_id=self.testuser1_id)
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))


    def test_add_like(self):
        m = Message(id=1234, text="The test message text", user_id=self.testuser1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = c.post("/users/add_like/1234", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(likes[0].user_id, self.testuser2_id)


    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=testuser1")

            self.assertIn("@testuser1", str(resp.data))
            self.assertNotIn("testuser2", str(resp.data))










