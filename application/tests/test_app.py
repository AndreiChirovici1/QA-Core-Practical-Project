from flask import url_for
from flask_testing import TestCase
from application import app, db
from application.models import users, accounts

class TestBase(TestCase):
    def create_app(self):
        app.config.update(
            SQLALCHEMY_DATABASE_URI = 'sqlite:///users.sqlite3',
            SECRET_KEY = 'averysecretkey1',
            DEBUG_MODE = True,
            WTF_CSRF_ENABLED = False
        )
        return app

    def setUp(self):
        db.create_all()
        test_user = users(firstname="James", surname="Smith", email="andrei.chirovici@gmail.com", dob="01/01/2000", securitycode="218292")
        db.session.add(test_user)
        db.session.commit()

def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestHome(TestBase):
    def test_home_get(self):
        response = self.client.get(url_for('home'))
        self.assert200(response)

class TestLogin(TestBase):
    def test_login_get(self):
        response = self.client.get(url_for('login'))
        self.assert200(response)

class TestLiveExchangeRates(TestBase):
    def test_liverates_get(self):
        response = self.client.get(url_for('latestrates'))
        self.assert200(response)

class TestContact(TestBase):
    def test_contact_get(self):
        response = self.client.get(url_for('contact'))
        self.assert200(response)

class TestAddUser(TestBase):
    def test_register_page(self):
        response = self.client.get(url_for('register'))
        self.assert200(response)
    
    def test_register_user(self):
        response = self.client.post(
            url_for('register'),
            data = dict(name="Andrei", email="andrei.chirovici@gmail.com"),
            follow_redirects = True
        )
        self.assert200(response)