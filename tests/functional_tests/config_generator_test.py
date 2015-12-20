"""
this test case verifies the functionality of the network configuration generator based on a selenium test case
"""
from tests import BaseFlaskLiveServerTest


class NetworkConfigurationGeneratorUseCaseTest(BaseFlaskLiveServerTest):

    def test_project_homepage_view(self):
        # open the homepage
        self.browser.get(self.get_server_url() + "/")

        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn("Network Configuration Generator", page_text)
