"""
basic view tests for the Flask application
"""
from tests import BaseFlaskTest
from flask import url_for


class CommonSiteTest(BaseFlaskTest):

    def test_redirect_of_the_homepage(self):
        """
        test redirect to homepage if connecting to the
        :return:
        """
        response = self.client.get("/")
        self.assertEqual(response.headers['Location'], "http://localhost%s" % url_for("home"))
        self.assertEqual(response.status_code, 302)

    def test_homepage_is_available(self):
        """
        just a simple test to avoid an error when accessing the homepage
        :return:
        """
        response = self.client.get(url_for("home"))
        self.assert200(response)
