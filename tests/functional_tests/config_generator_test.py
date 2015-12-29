"""
This test case verifies the basic functionality of the Web service based on a selenium test case
"""
from tests import BaseFlaskLiveServerTest


class NetworkConfigurationGeneratorUseCaseTest(BaseFlaskLiveServerTest):

    def test__create_a_template_project_and_basic_work_with_the_config_template(self):
        # test data
        test_project_name = "sample project"
        test_config_template_name = "sample configuration template"
        test_config_template_content = """!
!
!
! some configuration
!
!"""
        test_tvs1_hostname = "my-hostname"
        test_tvs2_hostname = "my-other-hostname"
        test_var_1_value = "Variable 1 value within the site"

        # open the homepage
        self.browser.get(self.get_server_url() + "/")

        # click on "view all projects link"
        self.browser.find_element_by_id("view_projects").click()

        # add a new project
        self.browser.find_element_by_id("create_project").click()
        self.browser.find_element_by_id("name").send_keys(test_project_name)
        self.browser.find_element_by_id("submit").click()

        # verify that the creation was successful
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_project_name, content)
        self.assertIn("Project %s successful created" % test_project_name, content)

        # create a new configuration template
        self.browser.find_element_by_id("create_config_templates").click()
        self.browser.find_element_by_id("name").send_keys(test_config_template_name)
        self.browser.find_element_by_id("template_content").send_keys(test_config_template_content)
        self.browser.find_element_by_id("submit").click()

        # verify configuration template detail view
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_config_template_name, content)
        self.assertIn(test_config_template_content, content)
        self.assertIn("var_1 first variable for the template", content)
        self.assertIn("var_2", content)
        self.assertIn("var_3 another description", content)

        # add new configuration template value set
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs1_hostname)
        self.browser.find_element_by_id("submit").click()

        # view the Template Value Set details
        self.browser.find_element_by_link_text(test_tvs1_hostname).click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_tvs1_hostname, content)
        self.assertIn("hostname %s" % test_tvs1_hostname, content)
        self.assertIn("var_1", content)
        self.assertIn("var_2", content)
        self.assertIn("var_3", content)

        # update a value of a variable
        self.browser.find_element_by_id("edit_template_value_set").click()
        self.browser.find_element_by_id("edit_var_1").send_keys(test_var_1_value)
        self.browser.find_element_by_id("submit").click()

        # verify result of the first configuration template value set in the detail view
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Template value set template successful saved", content)
        self.browser.find_element_by_link_text(test_tvs1_hostname).click()

        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("var_1 " + test_var_1_value, content)
        self.browser.find_element_by_id("_back").click()

        # go back to config template overview
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_config_template_name, content)
        self.assertIn("name var_1 var_2 var_3 action", content)
        self.assertIn(test_var_1_value, content)

        # add new configuration template value set
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs2_hostname)
        self.browser.find_element_by_id("submit").click()

        # verify result of the second configuration template value set in the detail view
        self.browser.find_element_by_link_text(test_tvs2_hostname).click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_tvs2_hostname, content)
        self.assertIn("hostname %s" % test_tvs2_hostname, content)
        self.assertIn("var_1", content)
        self.assertIn("var_2", content)
        self.assertIn("var_3", content)
        self.browser.find_element_by_id("_back").click()

        # add a description to the second variable
        new_description = "description for the second variable"
        self.browser.find_element_by_id("edit_variable_1").click()
        self.browser.find_element_by_id("description").send_keys(new_description)
        self.browser.find_element_by_id("submit").click()

        # verify result on the config template overview
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(new_description, content)

        # go back to config template
        self.browser.find_element_by_id("delete_template_value_set_1").click()
        self.browser.find_element_by_id("submit").click()

        # verify content
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Config Template %s successful deleted" % test_tvs1_hostname, content)
        self.assertIn(test_tvs2_hostname, content)

        # delete the other template view
        self.browser.find_element_by_id("delete_template_value_set_2").click()
        self.browser.find_element_by_id("submit").click()

        # verify results
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Config Template %s successful deleted" % test_tvs2_hostname, content)
        self.assertIn("There are not Template Value Sets defined.", content)
