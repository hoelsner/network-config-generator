"""
This test case verifies the basic functionality of the Web service based on a selenium test case
"""
import os
import time
from zipfile import ZipFile
from tests import BaseFlaskLiveServerTest


class NetworkConfigurationGeneratorUseCaseTest(BaseFlaskLiveServerTest):

    def test_create_a_template_project_and_basic_work_with_the_config_template(self):
        # test data
        test_project_name = "sample project"
        test_config_template_name = "sample configuration template"
        test_config_template_content = """## this is a sample config comment
!
!
!
! some configuration
!
first_value ${ var_1 }
second_value ${ var_2 }
third_value ${ var_3 }
!
!"""
        test_config_template_content_changed = """!
!
!
! changed configuration template
!
first_value ${ var_1 }
second_value ${ var_2 }
third_value ${ var_3 }
!
!"""
        test_tvs1_hostname = "my-hostname"
        test_tvs2_hostname = "my-other-hostname"
        test_var_1_value = "Variable 1 value within the site"
        first_config_content = "!\n!\n!\n! some configuration\n!\nfirst_value Variable 1 value within the site\n" \
                               "second_value \nthird_value \n!\n!"

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
        self.assertIn("var_1", content)
        self.assertIn("var_2", content)
        self.assertIn("var_3", content)

        # add new configuration template value set
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs1_hostname)
        self.browser.find_element_by_id("submit").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Template value set successful created", content)

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
        self.assertIn("name var_1 var_2 var_3", content)
        self.assertIn(test_var_1_value, content)

        # add new configuration template value set
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs2_hostname)
        self.browser.find_element_by_id("submit").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Template value set successful created", content)

        # verify result of the second configuration template value set in the detail view
        time.sleep(1)
        self.browser.find_element_by_link_text(test_tvs2_hostname).click()
        time.sleep(30)
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(test_tvs2_hostname, content)
        self.assertIn("hostname %s", content)
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

        # view the configuration of the first device
        self.browser.find_element_by_id("view_config_1").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn(first_config_content, content)
        self.browser.find_element_by_id("_back").click()

        # download the configuration of the first device
        self.browser.find_element_by_id("download_config_1").click()

        # wait for download complete
        time.sleep(1)

        # verify downloaded file
        expected_file = os.path.join(self.download_dir, test_tvs1_hostname + "_config.txt")
        self.assertTrue(os.path.exists(expected_file))
        self.assertTrue(os.path.isfile(expected_file))

        f = open(expected_file, "r")
        file_content = f.read()
        self.assertEqual(first_config_content, file_content)
        f.close()

        os.remove(expected_file)

        # download all configs and verify file
        self.browser.find_element_by_id("download_all_configurations").click()
        time.sleep(1)
        expected_file = os.path.join(self.download_dir, test_config_template_name + "_configs.zip")
        self.assertTrue(os.path.exists(expected_file))
        self.assertTrue(os.path.isfile(expected_file))

        zipfile = ZipFile(expected_file)
        zipfile.extractall(self.download_dir)

        expected_config_file = test_tvs1_hostname + "_config.txt"
        self.assertTrue(os.path.exists(os.path.join(self.download_dir, expected_config_file)))
        self.assertTrue(os.path.isfile(os.path.join(self.download_dir, expected_config_file)))

        f = open(os.path.join(self.download_dir, expected_config_file), "r")
        file_content = f.read()
        self.assertEqual(first_config_content, file_content)
        f.close()

        os.remove(os.path.join(self.download_dir, expected_config_file))
        os.remove(os.path.join(self.download_dir, test_tvs2_hostname + "_config.txt"))
        os.remove(expected_file)

        # change the configuration script
        self.browser.find_element_by_id("edit_template_value_set").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Edit the Config Template", content)
        self.assertIn(test_config_template_content, content)
        self.browser.find_element_by_id("template_content").clear()
        self.browser.find_element_by_id("template_content").send_keys(test_config_template_content_changed)
        self.browser.find_element_by_id("submit").click()

        # verify, that all template_value sets are deleted
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("There are not Template Value Sets defined.", content)

        # create the two value sets again
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs1_hostname)
        self.browser.find_element_by_id("submit").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Template value set successful created", content)
        self.browser.find_element_by_id("create_template_value_set").click()
        self.browser.find_element_by_id("hostname").send_keys(test_tvs2_hostname)
        self.browser.find_element_by_id("submit").click()
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Template value set successful created", content)

        # manually remove the template value set
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
