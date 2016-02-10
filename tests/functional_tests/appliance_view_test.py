"""
This test case verifies the appliance status view (status of the FTP, TFTP, redis-server and the celery worker service)

The following services must run prior starting the tests:

 * a local redis server (`$ redis-server`)
 * a celery worker thread (`(venv)$ celery worker -A app.celery --loglevel=debug`)

"""
import time

from tests import BaseFlaskLiveServerTest


class ApplianceViewTest(BaseFlaskLiveServerTest):

    def test_view_appliance_status(self):
        # open the homepage
        self.browser.get(self.get_server_url())

        # navigate to the
        self.browser.find_element_by_link_text("Appliance Status").click()

        # wait some time
        time.sleep(30)

        # verify that the redis server is started (check the ajax results)
        expected_html = '<span class="uk-icon-thumbs-up" id="redis_state" style="color: green;"></span>'
        content = self.browser.page_source
        self.assertIn(expected_html, content)

        # verfiy thet the local celery worker is started
        expected_html = '<span class="uk-icon-thumbs-up" id="celery_worker_state" style="color: green;"></span>'
        self.assertIn(expected_html, content)

        # create a test task
        self.browser.find_element_by_id("form_a").send_keys("4")
        self.browser.find_element_by_id("form_b").send_keys("6")
        self.browser.find_element_by_id("start-job").click()
        time.sleep(1)
        self.assertIn("calculating", self.browser.find_element_by_tag_name("body").text)

        # wait for task to complete
        time.sleep(3)

        # verify result
        self.assertIn("Sum: 10", self.browser.find_element_by_tag_name("body").text)
