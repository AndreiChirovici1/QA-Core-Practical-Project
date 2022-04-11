from flask import url_for
from flask_testing import TestCase
from application import app, db
from application.models import users, games

class TestBase(TestCase):
    def create_app(self):
        app.config.update(
            SQLALCHEMY_DATABASE_URI = 'sqlite:///test.sqlite3',
            SECRET_KEY = 'testsecretkey',
            DEBUG_MODE = True,
            WTF_CSRF_ENABLED = False
        )
        return app

    def setUp(self):
        db.create_all()
        test_user = users(name="Andrei", email="andrei.chirovici@gmail.com")
        db.session.add(test_user)
        db.session.commit()

def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestHome(TestBase):
    def test_home_get(self):
        response = self.client.get(url_for('home'))
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