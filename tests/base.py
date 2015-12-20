"""
base classes for Flask test cases using the Flask-Testing module
"""
from flask.ext.testing import TestCase, LiveServerTestCase
from selenium.webdriver.firefox import webdriver
from app import app, db


class BaseFlaskTest(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class BaseFlaskLiveServerTest(LiveServerTestCase):

    def create_app(self):
        app.config.from_object('config.LiveServerTestConfig')
        return app

    def setUp(self):
        db.create_all()
        self.browser = webdriver.WebDriver()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.browser.quit()
