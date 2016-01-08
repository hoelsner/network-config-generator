"""
base classes for Flask test cases using the Flask-Testing module
"""
import os
from flask.ext.testing import TestCase, LiveServerTestCase
from selenium.webdriver.firefox import webdriver
from app import app, db
from config import APP_BASE_DIR


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

    download_dir = os.path.join(APP_BASE_DIR, "tests", "_selenium", "downloads")

    def create_app(self):
        app.config.from_object('config.LiveServerTestConfig')
        return app

    def setUp(self):
        db.create_all()

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", self.download_dir)
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "text/plain,text/csv,text/html,application/zip"
        )
        self.browser = webdriver.WebDriver(firefox_profile=profile)
        self.browser.implicitly_wait(3)
        self.browser.set_window_size(1280, 1024)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.browser.quit()
