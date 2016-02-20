"""
basic view tests for the Flask application
"""
import json
import os
import shutil

import time
from flask import url_for
from slugify import slugify

from app import db, app
from app.models import Project, ConfigTemplate, TemplateValueSet, TemplateVariable
from tests import BaseFlaskTest


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

    def test_how_to_use_page_is_available(self):
        """
        just a simple test to avoid an error when accessing the how to use page
        :return:
        """
        response = self.client.get(url_for("how_to_use"))
        self.assert200(response)

    def test_template_syntax_page_is_available(self):
        """
        just a simple test to avoid an error when accessing the template syntax page
        :return:
        """
        response = self.client.get(url_for("template_syntax"))
        self.assert200(response)

    def test_verify_appliance_status(self):
        """
        just a simple test to avoid an error when accessing the appliance status page
        :return:
        """
        response = self.client.get(url_for("appliance_status"))
        self.assert200(response)

    def test_appliance_status_json(self):
        """
        test the json response of the appliance status Ajax endpoint
        :return:
        """
        response = self.client.get(url_for("appliance_status_json"))
        self.assert200(response)

        content = json.loads(response.data.decode("utf-8"))
        self.assertTrue("ftp" in content.keys())
        self.assertTrue("tftp" in content.keys())
        self.assertTrue("redis" in content.keys())
        self.assertTrue("celery_worker" in content.keys())


class ProjectViewTest(BaseFlaskTest):

    def setUp(self):
        # disable CSRF for unit testing
        super().setUp()
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_view_all_projects(self):
        """
        test view all projects page
        :return:
        """
        # test empty view
        response = self.client.get(url_for("view_all_projects"))
        self.assert200(response)
        self.assertTemplateUsed("project/view_all_projects.html")
        self.assertIn("No Projects found in database.", response.data.decode("utf-8"))

        # test view with elements
        project_names = [
            "My first Project",
            "My second Project",
            "My third Project",
        ]
        for name in project_names:
            p = Project(name)
            db.session.add(p)
            db.session.commit()

        response = self.client.get(url_for("view_all_projects"))
        self.assert200(response)
        self.assertTemplateUsed("project/view_all_projects.html")
        self.assertTrue(len(Project.query.all()) > 0)

        for name in project_names:
            self.assertIn(name, response.data.decode("utf-8"))

    def test_view_project_success(self):
        """
        test project view
        :return:
        """
        p = Project("My Project")
        db.session.add(p)
        db.session.commit()

        response = self.client.get(url_for("view_project", project_id=p.id))
        self.assert200(response)
        self.assertTemplateUsed("project/view_project.html")
        self.assertIn(p.name, response.data.decode("utf-8"))

    def test_view_project_404(self):
        """
        test project view not found
        :return:
        """
        response = self.client.get(url_for("view_project", project_id=9999))
        self.assert404(response)

    def test_valid_config_template_name(self):
        """Test the validate Config Template name function of the Project class

        :return:
        """
        p = Project("project")
        ct = ConfigTemplate("ct", project=p)

        db.session.add_all([p, ct])

        self.assertFalse(p.valid_config_template_name(None))
        self.assertFalse(p.valid_config_template_name(""))
        self.assertFalse(p.valid_config_template_name("ct"))
        self.assertTrue(p.valid_config_template_name("ct1"))

    def test_add_project(self):
        """
        add new project
        :return:
        """
        project_name = "My Project"
        data = {
            "name": project_name
        }

        # add a new project
        response = self.client.post(url_for("add_project"), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertIn(project_name, response.data.decode("utf-8"))
        self.assertTemplateUsed("project/view_project.html")
        self.assertTrue(len(Project.query.all()) == 1)

        p = Project.query.filter(Project.name == project_name).first()

        self.assertIsNotNone(p, "Project not found and was therefore not created")
        self.assertEqual(p.name, project_name)

    def test_edit_project(self):
        """
        test edit of the project data object (including renaming of the project)
        :return:
        """
        project_name = "project name"
        conflicting_project_name = "conflicting project name"
        renamed_project_name = "renamed project name"
        p1 = Project(project_name)
        p2 = Project(conflicting_project_name)
        db.session.add_all([p1, p2])
        db.session.commit()

        # try to change the name of p1 (same name as p2)
        data = {
            "name": conflicting_project_name
        }
        response = self.client.post(url_for("edit_project", project_id=p1.id), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertTemplateUsed("project/edit_project.html")
        self.assertTrue(len(Project.query.all()) == 2)
        self.assertIn("Project name already in use, please use another one", response.data.decode("utf-8"))

        p = Project.query.filter(Project.name == project_name).first()

        self.assertIsNotNone(p, "Project not found in database")
        self.assertEqual(p.name, project_name)

        # test rename project
        data = {
            "name": renamed_project_name
        }
        response = self.client.post(url_for("edit_project", project_id=p.id), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertTemplateUsed("project/view_project.html")
        self.assertTrue(len(Project.query.all()) == 2)
        self.assertIn(renamed_project_name, response.data.decode("utf-8"))

        p = Project.query.filter(Project.name == renamed_project_name).first()

        self.assertIsNotNone(p, "Renamed Project not found in database")
        self.assertEqual(p.name, renamed_project_name)

    def test_edit_project_attributes(self):
        """
        test edit of the project attributes
        :return:
        """
        project_name = "project name"
        p = Project(project_name)
        db.session.add(p)
        db.session.commit()

        # test project edit form
        data = {
            "name": project_name
        }
        response = self.client.post(url_for("edit_project", project_id=p.id), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertTemplateUsed("project/view_project.html")
        self.assertTrue(len(Project.query.all()) == 1)

    def test_delete_project_success(self):
        """
        test successful deletion operation on a project
        :return:
        """
        p = Project("My Project")
        db.session.add(p)
        db.session.commit()

        # delete the element
        response = self.client.get(url_for("delete_project", project_id=p.id), follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed("project/delete_project.html")
        delete_message = "Do you really want to delete this <strong>Project</strong>?"
        self.assertIn(delete_message, response.data.decode("utf-8"))

        response = self.client.post(url_for("delete_project", project_id=p.id), follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed("project/view_all_projects.html")
        self.assertIn("All Projects", response.data.decode("utf-8"))
        self.assertTrue(len(Project.query.all()) == 0)

    def test_delete_project_failed(self):
        """
        test a failed deletion operation on a project
        :return:
        """
        response = self.client.get(url_for("delete_project", project_id=999), follow_redirects=True)
        self.assert404(response)


class ConfigTemplateViewTest(BaseFlaskTest):

    def setUp(self):
        # disable CSRF for unit testing
        super().setUp()
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_view_all_config_templates(self):
        """
        test view all config template page (integrated to the view project)
        :return:
        """
        project_name = "My Project"
        project_template_names = [
            "first template",
            "second template",
            "third template",
        ]
        ct_other_name = "template not visible in p1"
        p1 = Project(project_name)
        p2 = Project("My other Project")
        db.session.add_all([p1, p2])

        for name in project_template_names:
            ct = ConfigTemplate(name=name, project=p1)
            db.session.add(ct)
            db.session.commit()
        ct_other = ConfigTemplate(name=ct_other_name, project=p2)
        db.session.add(ct_other)
        db.session.commit()

        response = self.client.get(url_for("view_project", project_id=p1.id))
        self.assert200(response)
        self.assertTemplateUsed("project/view_project.html")
        self.assertTrue(len(Project.query.all()) >= 2)
        self.assertTrue(len(ConfigTemplate.query.all()) >= 4)

        for name in project_template_names:
            self.assertIn(name, response.data.decode("utf-8"))

        # the template is visible in the sidebar, ensure that this is not the case for the first project
        self.assertNotIn(
                '<a href="/ncg/project/1/template/4">\n<span class="uk-icon-file"></span>\n%s' % ct_other_name,
                response.data.decode("utf-8")
        )

    def test_view_config_template_success(self):
        """
        test config template view
        :return:
        """
        var_1_name = "variable_1"
        var_1_desc = "description 1"
        var_2_name = "variable_2"
        var_2_desc = "description 2"
        template_content = "${ %s } ${ %s }" % (var_1_name, var_2_name)

        p = Project("My Project")
        ct = ConfigTemplate("Template name", project=p, template_content=template_content)

        ct.update_template_variable(var_1_name, var_1_desc)
        ct.update_template_variable(var_2_name, var_2_desc)
        db.session.add(p)
        db.session.add(ct)
        db.session.commit()

        response = self.client.get(url_for("view_config_template", project_id=p.id, config_template_id=ct.id))
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertIn(ct.name, response.data.decode("utf-8"))
        self.assertIn(var_1_name, response.data.decode("utf-8"))
        self.assertIn(var_1_desc, response.data.decode("utf-8"))
        self.assertIn(var_2_name, response.data.decode("utf-8"))
        self.assertIn(var_2_desc, response.data.decode("utf-8"))

    def test_view_config_template_404(self):
        """
        test config template view not found
        :return:
        """
        p = Project("My project")
        db.session.add(p)
        db.session.commit()
        response = self.client.get(
                url_for(
                    "view_config_template",
                    project_id=p.id,
                    config_template_id=9999
                )
        )
        self.assert404(response)

    def test_add_config_template(self):
        """
        add new config template
        :return:
        """
        p = Project("Name")
        db.session.add(p)
        db.session.commit()

        config_template_name = "My Template name"
        config_template_content = """!
!
! Test template
!
!"""
        data = {
            "name": config_template_name,
            "template_content": config_template_content
        }

        # add a new config template
        response = self.client.post(url_for("add_config_template", project_id=p.id), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertIn(config_template_name, response.data.decode("utf-8"))
        self.assertIn(config_template_content, response.data.decode("utf-8"))
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(Project.query.all()) == 1)

        ct = ConfigTemplate.query.filter(
                (ConfigTemplate.name == config_template_name) and
                (ConfigTemplate.project.id == p.id)
        ).first()

        self.assertIsNotNone(ct, "Config Template not found and was therefore not created")
        self.assertEqual(ct.name, config_template_name)

    def test_add_config_template_with_invalid_syntax(self):
        """
        add new config template with invalid syntax
        :return:
        """
        p = Project("Name")
        db.session.add(p)
        db.session.commit()

        config_template_name = "My Template name"
        config_template_content = """!
!
! Test template
!
% if:
something
% else
nothing (there is the error)
% endif
!"""
        data = {
            "name": config_template_name,
            "template_content": config_template_content
        }

        # add a new project
        response = self.client.post(url_for("add_config_template", project_id=p.id), data=data, follow_redirects=True)

        self.assert200(response)
        self.assertIn("Invalid template, please correct the following error: ", response.data.decode("utf-8"))
        self.assertTemplateUsed("config_template/add_config_template.html")
        self.assertTrue(len(ConfigTemplate.query.all()) == 0)

    def test_edit_config_template(self):
        """
        test edit of the config template data object (including renaming of the project)
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        changed_ct_content = "changed content"
        conflicting_ct_name = "conflicting config template name"
        renamed_ct_name = "renamed config template name"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        ct2 = ConfigTemplate(name=conflicting_ct_name, template_content=ct_content, project=p)
        db.session.add_all([ct1, ct2])
        db.session.commit()

        # try to change the name of ct1 (same name as ct2)
        data = {
            "name": conflicting_ct_name,
            "template_content": ct_content
        }
        response = self.client.post(
            url_for(
                "edit_config_template",
                project_id=ct1.project.id,
                config_template_id=ct1.id),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/edit_config_template.html")
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)
        self.assertIn("Config Template name already in use, please use another one", response.data.decode("utf-8"))

        ct1 = ConfigTemplate.query.filter(
                (Project.id == p.id) and
                (ConfigTemplate.name == ct_name)
        ).first()

        self.assertIsNotNone(ct1, "Config Template not found in database")
        self.assertEqual(ct1.name, ct_name)
        self.assertEqual(ct1.template_content, ct_content)

        # test rename of Config Template
        data = {
            "name": renamed_ct_name,
            "template_content": changed_ct_content
        }
        response = self.client.post(
            url_for(
                "edit_config_template",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)
        self.assertIn(renamed_ct_name, response.data.decode("utf-8"))
        self.assertIn(changed_ct_content, response.data.decode("utf-8"))

        ct = ConfigTemplate.query.filter(
                (ConfigTemplate.name == renamed_ct_name) and
                (ConfigTemplate.project.id == p.id)
        ).first()

        self.assertIsNotNone(ct, "Renamed Config Template not found")
        self.assertEqual(ct.name, renamed_ct_name)

    def test_edit_config_template_attributes(self):
        """
        test edit of the config template attributes
        :return:
        """
        project_name = "project name"
        p = Project(project_name)
        db.session.add(p)
        db.session.commit()

        ct = ConfigTemplate(name="mytemplate", template_content="The is the content", project=p)
        db.session.add(ct)
        db.session.commit()

        new_ct_content = "other content than before"

        # test project edit form
        data = {
            "name": ct.name,
            "template_content": new_ct_content
        }
        response = self.client.post(
            url_for(
                "edit_config_template",
                project_id=p.id,
                config_template_id=ct.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertIn(new_ct_content, response.data.decode("utf-8"))

    def test_delete_config_template_success(self):
        """
        test successful deletion operation on a config template
        :return:
        """
        p = Project("My Project")
        ct1 = ConfigTemplate("config template", project=p)
        ct2 = ConfigTemplate("another config template", project=p)
        db.session.add_all([p, ct1, ct2])
        db.session.commit()
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)

        # delete the element
        response = self.client.get(
                url_for(
                    "delete_config_template",
                    project_id=ct1.project.id,
                    config_template_id=ct1.id
                ),
                follow_redirects=True
        )
        self.assert200(response)
        delete_message = "Do you really want to delete this <strong>Config Template</strong>?"
        self.assertIn(delete_message, response.data.decode("utf-8"))

        response = self.client.post(
                url_for(
                    "delete_config_template",
                    project_id=ct1.project.id,
                    config_template_id=ct1.id
                ),
                follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("project/view_project.html")
        self.assertIn("View Project", response.data.decode("utf-8"))
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(len(Project.query.all()) == 1)

    def test_delete_config_template_failed(self):
        """
        test a failed deletion operation on a config template
        :return:
        """
        p = Project("My project")
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for("delete_config_template", project_id=p.id, config_template_id=9999))
        self.assert404(response)

    def test_rename_variable_description_in_the_config_template(self):
        """
        rename a Config Template variable description using the form
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        changed_description = "changed description with some custom content"

        p = Project(project_name)
        db.session.add(p)

        ct = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        ct.update_template_variable("var_1")
        db.session.add(ct)

        data = {
            "var_name_slug": "var_1",
            "description": changed_description
        }
        response = self.client.post(
            url_for(
                "edit_template_variable",
                config_template_id=ct.id,
                template_variable_id=ct.get_template_variable_by_name("var_1").id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateVariable.query.all()) == 1+1)
        self.assertIn(changed_description, response.data.decode("utf-8"))

    def test_rename_of_a_variable_with_an_reserved_name(self):
        """
        the variable cannot be renamed to "hostname" because it is reserved
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        p = Project(project_name)
        db.session.add(p)

        ct = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        ct.update_template_variable("var_1")
        db.session.add(ct)

        data = {
            "var_name_slug": "hostname"
        }
        response = self.client.post(
            url_for(
                "edit_template_variable",
                config_template_id=ct.id,
                template_variable_id=ct.get_template_variable_by_name("var_1").id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("template_variable/edit_template_variable.html")
        self.assertTrue(len(TemplateVariable.query.all()) == 1+1)
        self.assertIn(
                "hostname is reserved by the application, please choose another one",
                response.data.decode("utf-8")
        )

    def test_rename_of_a_variable_within_the_config_template(self):
        """
        test rename of a template variable
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        p = Project(project_name)
        changed_var_name = "var_1_changed"
        db.session.add(p)

        ct = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        ct.update_template_variable("var_1")
        db.session.add(ct)

        # try to change the name of a variables
        data = {
            "var_name_slug": changed_var_name
        }
        response = self.client.post(
            url_for(
                "edit_template_variable",
                config_template_id=ct.id,
                template_variable_id=ct.get_template_variable_by_name("var_1").id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateVariable.query.all()) == 1+1)
        self.assertIn(changed_var_name, response.data.decode("utf-8"))

    def test_valid_template_value_set_name(self):
        """Test the validate Template Value Set name function of the Config Template class

        :return:
        """
        p = Project("project")
        ct = ConfigTemplate("ct", project=p)
        tvs = TemplateValueSet("tvs", config_template=ct)

        db.session.add_all([p, ct, tvs])

        self.assertFalse(ct.valid_template_value_set_name(None))
        self.assertFalse(ct.valid_template_value_set_name(""))
        self.assertFalse(ct.valid_template_value_set_name("tvs"))
        self.assertTrue(ct.valid_template_value_set_name("tvs1"))

    def test_add_template_value_sets_using_the_csv_form(self):
        """Test the bulk creation of Template Value Sets using the CSV form

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n" \
                  "host_D;4;44;444\n" \
                  "host_E;5;55;555\n" \
                  "host_F;6;66;666\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        db.session.add(ct1)
        db.session.commit()

        response = self.client.get(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            )
        )
        self.assert200(response)

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 6)

        # verify result
        tvs = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_C",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(tvs, "Object not found, CVS parsing failed")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_one"), "3")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_two"), "33")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_three"), "333")

        tvs = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_E",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(tvs, "Object not found, CVS parsing failed")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_one"), "5")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_two"), "55")
        self.assertEqual(tvs.get_template_value_by_name_as_string("variable_three"), "555")

    def test_add_template_value_sets_with_additional_variables_in_header(self):
        """Test the bulk creation of Template Value Sets using the CSV form with additional variables (should be
        silently ignored).

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three;additional_var\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        tvs1 = TemplateValueSet(hostname="host_A", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="host_B", config_template=ct1)
        tvs3 = TemplateValueSet(hostname="host_C", config_template=ct1)
        db.session.add_all([ct1, tvs1, tvs2, tvs3])
        db.session.commit()

        response = self.client.get(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            )
        )
        self.assert200(response)

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 3)
        # no messages should be visible after submitting the CSV content
        self.assertNotIn('<ul class="flashes">', response.data.decode("utf-8"))

    def test_add_template_value_sets_with_less_variables_in_header(self):
        """Test the bulk creation of Template Value Sets using the CSV form with less variables (silently ignored)

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two\n" \
                  "host_A;1;11\n" \
                  "host_B;2;22\n" \
                  "host_C;3;33\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        tvs1 = TemplateValueSet(hostname="host_A", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="host_B", config_template=ct1)
        tvs3 = TemplateValueSet(hostname="host_C", config_template=ct1)
        db.session.add_all([ct1, tvs1, tvs2, tvs3])
        db.session.add(ct1)
        db.session.commit()

        response = self.client.get(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            )
        )
        self.assert200(response)

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 3)
        # no messages should be visible after submitting the CSV content
        self.assertNotIn('<ul class="flashes">', response.data.decode("utf-8"))

    def test_add_template_value_sets_using_the_csv_form_with_invalid_hostname(self):
        """Test the failed creation of Template Value Sets with an invalid hostname using the CSV form

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n" \
                  "host_D;4;44;444\n" \
                  ";5;55;555\n" \
                  "host_F;6;66;666\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        db.session.add(ct1)
        db.session.commit()

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 5)
        self.assertIn("No Hostname defined for Template Value Set", response.data.decode("utf-8"))

    def test_edit_template_value_sets_using_the_csv_form(self):
        """Test the bulk edit of Template Value Sets using the CSV form

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n" \
                  "host_D;4;44;444\n" \
                  "host_E;5;55;555\n" \
                  "host_F;6;66;666\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        db.session.add(ct1)

        tvs1 = TemplateValueSet(hostname="host_A", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="host_B", config_template=ct1)
        tvs3 = TemplateValueSet(hostname="host_C", config_template=ct1)
        tvs4 = TemplateValueSet(hostname="host_D", config_template=ct1)
        tvs5 = TemplateValueSet(hostname="host_E", config_template=ct1)
        tvs6 = TemplateValueSet(hostname="host_F", config_template=ct1)

        db.session.add_all([tvs1, tvs2, tvs3, tvs4, tvs5, tvs6])
        db.session.commit()

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 6)

        received_tvs3 = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_C",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(received_tvs3, "Object not found in database")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_one"), "3")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_two"), "33")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_three"), "333")

        received_tvs5 = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_E",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(received_tvs5, "Object not found in database")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_one"), "5")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_two"), "55")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_three"), "555")

    def test_add_and_edit_template_value_sets_using_the_csv_form(self):
        """Test the bulk add and edit of Template Value Sets using the CSV form

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n" \
                  "host_D;4;44;444\n" \
                  "host_E;5;55;555\n" \
                  "host_F;6;66;666\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        db.session.add(ct1)

        tvs1 = TemplateValueSet(hostname="host_A", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="host_B", config_template=ct1)
        tvs3 = TemplateValueSet(hostname="host_C", config_template=ct1)
        tvs4 = TemplateValueSet(hostname="host_D", config_template=ct1)
        tvs6 = TemplateValueSet(hostname="host_F", config_template=ct1)

        db.session.add_all([tvs1, tvs2, tvs3, tvs4, tvs6])
        db.session.commit()

        data = {
            "csv_content": tvs_csv
        }
        response = self.client.post(
            url_for(
                "edit_all_config_template_values",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            ),
            data=data,
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 6)

        received_tvs3 = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_C",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(received_tvs3, "Object not found in database")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_one"), "3")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_two"), "33")
        self.assertEqual(received_tvs3.get_template_value_by_name_as_string("variable_three"), "333")

        received_tvs5 = TemplateValueSet.query.filter(
            TemplateValueSet.hostname == "host_E",
            TemplateValueSet.config_template == ct1
        ).first()

        self.assertIsNotNone(received_tvs5, "Object not found in database")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_one"), "5")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_two"), "55")
        self.assertEqual(received_tvs5.get_template_value_by_name_as_string("variable_three"), "555")

    def test_export_configurations_view(self):
        """simple test to avoid errors in the view

        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "template content:\n${variable_one}\n${variable_two}\n${variable_three}"
        tvs_csv = "hostname;variable_one;variable_two;variable_three;additional_var\n" \
                  "host_A;1;11;111\n" \
                  "host_B;2;22;222\n" \
                  "host_C;3;33;333\n"
        p = Project(project_name)
        db.session.add(p)

        ct1 = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        tvs1 = TemplateValueSet(hostname="host_A", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="host_B", config_template=ct1)
        tvs3 = TemplateValueSet(hostname="host_C", config_template=ct1)
        db.session.add_all([ct1, tvs1, tvs2, tvs3])
        db.session.commit()

        response = self.client.get(
            url_for(
                "export_configurations",
                project_id=ct1.project.id,
                config_template_id=ct1.id
            )
        )
        self.assert200(response)


class TemplateValueSetViewTest(BaseFlaskTest):

    def setUp(self):
        # disable CSRF for unit testing
        super().setUp()
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_view_all_template_value_set(self):
        """
        test view all template value sets (integrated to the view config template)
        :return:
        """
        p = Project("Test")
        template_name = "My Project"
        tvs_names = [
            "first template",
            "second template",
            "third template",
        ]
        tvs_other_name = "template not visible in ct1"
        ct1 = ConfigTemplate(name=template_name, project=p)
        ct2 = ConfigTemplate(name="other config template", project=p)
        db.session.add_all([p, ct1, ct2])

        for name in tvs_names:
            tvs = TemplateValueSet(hostname=name, config_template=ct1)
            db.session.add(tvs)
            db.session.commit()
        tvs_other = TemplateValueSet(hostname=tvs_other_name, config_template=ct2)
        db.session.add(tvs_other)
        db.session.commit()

        response = self.client.get(url_for("view_config_template", project_id=p.id, config_template_id=ct1.id))
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)
        self.assertTrue(len(TemplateValueSet.query.all()) == 4)

        for name in tvs_names:
            self.assertIn(name, response.data.decode("utf-8"))

        self.assertNotIn(tvs_other_name, response.data.decode("utf-8"))

    def test_view_template_value_set_success(self):
        """
        test template value set view
        :return:
        """
        p = Project("My Project")
        ct = ConfigTemplate("Template name", project=p)
        ct.update_template_variable(var_name="var 1")
        ct.update_template_variable(var_name="var 2")
        ct.update_template_variable(var_name="var 3")
        tvs1 = TemplateValueSet("Template 1", config_template=ct)
        tvs2 = TemplateValueSet("Template 2", config_template=ct)

        db.session.add_all([p, ct, tvs1, tvs2])
        db.session.commit()

        response = self.client.get(
            url_for(
                "view_template_value_set",
                config_template_id=ct.id,
                template_value_set_id=tvs1.id
            )
        )
        self.assert200(response)
        self.assertTemplateUsed("template_value_set/view_template_value_set.html")
        self.assertIn(tvs1.hostname, response.data.decode("utf-8"))
        self.assertIn("var_1", response.data.decode("utf-8"))
        self.assertIn("var_2", response.data.decode("utf-8"))

    def test_view_template_value_set_404(self):
        """
        test template value set view not found
        :return:
        """
        p = Project(name="Project")
        ct = ConfigTemplate(name="TemplateValueSet", project=p)
        db.session.add(p)
        db.session.add(ct)
        db.session.commit()
        response = self.client.get(
                url_for(
                    "view_template_value_set",
                    config_template_id=ct.id,
                    template_value_set_id=9999
                )
        )
        self.assert404(response)

    def test_add_template_value_set(self):
        """
        add new template value set
        :return:
        """
        p = Project("Name")
        ct = ConfigTemplate(name="Config Template", project=p)
        ct.update_template_variable("Key 1")
        ct.update_template_variable("Key 2")
        db.session.add_all([p, ct])
        db.session.commit()

        tvs_hostname = "Template Value set"
        data = {
            "hostname": tvs_hostname,
            "edit_hostname": tvs_hostname,
            "edit_key_1": "",
            "edit_key_2": ""
        }

        # add a new template value set
        response = self.client.post(
            url_for(
                "add_template_value_set",
                project_id=ct.project.id,
                config_template_id=ct.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertIn(tvs_hostname, response.data.decode("utf-8"))
        self.assertTemplateUsed("template_value_set/edit_template_value_set.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 1)

        tvs = TemplateValueSet.query.filter(
                (TemplateValueSet.hostname == tvs_hostname) and
                (TemplateValueSet.config_template.id == ct.id)
        ).first()

        self.assertIsNotNone(tvs, "Config Template not found and was therefore not created")
        self.assertEqual(tvs.hostname, tvs_hostname)
        self.assertTrue(tvs.is_value_defined("hostname"))
        self.assertEqual(tvs.get_template_value_by_name_as_string("hostname"), tvs.hostname)
        self.assertTrue(tvs.is_value_defined(tvs.convert_variable_name("Key 1")))
        self.assertTrue(tvs.is_value_defined(tvs.convert_variable_name("Key 2")))

    def test_edit_template_value_set(self):
        """
        test edit of the template value set data object (including renaming of the project)
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        tvs_name = "template value set"
        conflicting_tvs_name = "conflicting template value set"
        renamed_tvs_name = "renamed template value set"
        template_variables = (
            ("variable_1", "value for the first var"),
            ("variable_2", ""),
            ("variable_3", ""),
        )

        p = Project(project_name)
        db.session.add(p)

        ct = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        for name, value in template_variables:
            # disable the automatic conversion of the variable name
            self.assertEqual(ct.update_template_variable(name, value, auto_convert_var_name=False), name)
        db.session.add(ct)

        tvs1 = TemplateValueSet(hostname=tvs_name, config_template=ct)
        tvs2 = TemplateValueSet(hostname=conflicting_tvs_name, config_template=ct)
        db.session.add_all([tvs1, tvs2])
        db.session.commit()

        # try to change the name of tvs1 to tvs2
        data = {
            "hostname": conflicting_tvs_name
        }
        response = self.client.post(
            url_for(
                "edit_template_value_set",
                config_template_id=tvs1.config_template.id,
                template_value_set_id=tvs1.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("template_value_set/edit_template_value_set.html")
        self.assertIn("Template Value Set hostname already in use, please use another one", response.data.decode("utf-8"))
        self.assertTrue(len(TemplateValueSet.query.all()) == 2)

        tvs1 = TemplateValueSet.query.filter(
                (ConfigTemplate.id == ct.id) and
                (TemplateValueSet.hostname == tvs_name)
        ).first()

        self.assertIsNotNone(tvs1, "Template value set not found in database")
        self.assertEqual(tvs1.hostname, tvs_name)
        self.assertTrue(len(tvs1.values.all()) == 3+1)      # hostname is automatically added

        # test rename of Config Template
        data = {
            "hostname": renamed_tvs_name,
            "edit_hostname": tvs_name,
            "edit_variable_1": tvs1.get_template_value_by_name_as_string("variable_1"),
            "edit_variable_2": tvs1.get_template_value_by_name_as_string("variable_2"),
            "edit_variable_3": tvs1.get_template_value_by_name_as_string("variable_3"),
        }
        response = self.client.post(
            url_for(
                "edit_template_value_set",
                config_template_id=tvs1.config_template.id,
                template_value_set_id=tvs1.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertNotIn("Template Value set was not created (unknown error)", response.data.decode("utf-8"))
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 2)
        self.assertIn(renamed_tvs_name, response.data.decode("utf-8"))

        tvs = TemplateValueSet.query.filter(
                (TemplateValueSet.hostname == renamed_tvs_name) and
                (TemplateValueSet.config_template.id == ct.id)
        ).first()

        self.assertIsNotNone(tvs, "Renamed Config Template not found")
        self.assertEqual(tvs.hostname, renamed_tvs_name)

    def test_edit_template_value_set_attributes(self):
        """
        test edit of the template value set attributes
        :return:
        """
        project_name = "project name"
        ct_name = "template name"
        ct_content = "content"
        tvs_name = "template value set"
        conflicting_tvs_name = "conflicting template value set"
        renamed_tvs_name = "renamed template value set"
        template_variables = (
            ("variable_1", "value for the first var"),
            ("variable_2", ""),
            ("variable_3", ""),
        )

        p = Project(project_name)
        db.session.add(p)

        ct = ConfigTemplate(name=ct_name, template_content=ct_content, project=p)
        for name, value in template_variables:
            # disable the automatic conversion of the variable name
            self.assertEqual(ct.update_template_variable(name, value, auto_convert_var_name=False), name)
        db.session.add(ct)

        tvs1 = TemplateValueSet(hostname=tvs_name, config_template=ct)
        tvs2 = TemplateValueSet(hostname=conflicting_tvs_name, config_template=ct)
        db.session.add_all([tvs1, tvs2])
        db.session.commit()

        # test project edit form
        new_var_3_content = "other value than before"

        data = {
            "hostname": renamed_tvs_name,
            "edit_hostname": tvs_name,
            "edit_variable_1": tvs1.get_template_value_by_name_as_string("variable_1"),
            "edit_variable_2": tvs1.get_template_value_by_name_as_string("variable_2"),
            "edit_variable_3": new_var_3_content,
        }
        response = self.client.post(
            url_for(
                "edit_template_value_set",
                config_template_id=tvs1.config_template.id,
                template_value_set_id=tvs1.id
            ),
            data=data,
            follow_redirects=True
        )

        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertTrue(len(TemplateValueSet.query.all()) == 2)
        self.assertIn(new_var_3_content, response.data.decode("utf-8"))

    def test_delete_template_value_set_success(self):
        """
        test successful deletion operation on a template value set
        :return:
        """
        p = Project("My Project")
        ct = ConfigTemplate("config template", project=p)
        tvs1 = TemplateValueSet(hostname="Test 1", config_template=ct)
        tvs2 = TemplateValueSet(hostname="Test 2", config_template=ct)
        db.session.add_all([p, ct, tvs1, tvs2])
        db.session.commit()
        self.assertTrue(len(TemplateValueSet.query.all()) == 2)

        # delete the element
        response = self.client.get(
                url_for(
                    "delete_template_value_set",
                    config_template_id=ct.id,
                    template_value_set_id=tvs1.id
                )
        )
        self.assert200(response)
        self.assertTemplateUsed("template_value_set/delete_template_value_set.html")
        delete_message = "Do you really want to delete this Template Value Set? All associated " \
                         "elements are also deleted."
        self.assertIn(delete_message, response.data.decode("utf-8"))

        response = self.client.post(
                url_for(
                    "delete_template_value_set",
                    config_template_id=ct.id,
                    template_value_set_id=tvs1.id
                ),
                follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed("config_template/view_config_template.html")
        self.assertIn("View Config Template", response.data.decode("utf-8"))
        self.assertTrue(len(TemplateValueSet.query.all()) == 1)
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)

    def test_delete_template_value_set_failed(self):
        """
        test a failed deletion operation on a template value set
        :return:s
        """
        p = Project(name="Project")
        ct = ConfigTemplate("config template", project=p)
        db.session.add(p)
        db.session.add(ct)
        db.session.commit()
        response = self.client.get(
            url_for(
                "delete_template_value_set",
                config_template_id=ct.id,
                template_value_set_id=9999
            )
        )
        self.assert404(response)


class ConfigurationViewTest(BaseFlaskTest):

    def test_show_valid_configuration(self):
        """test configuration result

        :return:
        """
        var_1_name = "variable_1"
        var_1_desc = "description 1"
        var_2_name = "variable_2"
        var_2_desc = "description 2"
        first_hostname = "hostname_A"
        second_hostname = "hostname_B"
        template_content = "!\n${hostname}\n!\n${ %s }\n${ %s }" % (var_1_name, var_2_name)
        first_expected_result = "!\n%s\n!\n%s\n%s" % (first_hostname, "first value", "second value")
        second_expected_result = "!\n%s\n!\n%s\n%s" % (second_hostname, "first value", "second value")

        p = Project("My Project")
        ct = ConfigTemplate("Template name", project=p, template_content=template_content)

        ct.update_template_variable(var_1_name, var_1_desc)
        ct.update_template_variable(var_2_name, var_2_desc)

        tvs1 = TemplateValueSet(hostname=first_hostname, config_template=ct)
        tvs1.update_variable_value(var_1_name, "first value")
        tvs1.update_variable_value(var_2_name, "second value")
        tvs2 = TemplateValueSet(hostname=second_hostname, config_template=ct)
        tvs2.update_variable_value(var_1_name, "first value")
        tvs2.update_variable_value(var_2_name, "second value")

        db.session.add(p)
        db.session.add(ct)
        db.session.add(tvs1)
        db.session.add(tvs2)
        db.session.commit()

        # get configuration and check results
        response = self.client.get(url_for("view_config", config_template_id=ct.id, template_value_set_id=tvs1.id))
        self.assert200(response)
        self.assertIn(first_expected_result, response.data.decode("utf-8"))

        response = self.client.get(url_for("view_config", config_template_id=ct.id, template_value_set_id=tvs2.id))
        self.assert200(response)
        self.assertIn(second_expected_result, response.data.decode("utf-8"))

        # test download views
        response = self.client.get(url_for("download_config", config_template_id=ct.id, template_value_set_id=tvs1.id))
        self.assert200(response)
        self.assertTrue(first_expected_result == response.data.decode("utf-8"))

        response = self.client.get(url_for("download_config", config_template_id=ct.id, template_value_set_id=tvs2.id))
        self.assert200(response)
        self.assertTrue(second_expected_result == response.data.decode("utf-8"))

    def test_download_all_configurations(self):
        """test download of all configurations (only the creation of the ZIP archive, not the content itself)

        :return:
        """
        var_1_name = "variable_1"
        var_1_desc = "description 1"
        var_2_name = "variable_2"
        var_2_desc = "description 2"
        first_hostname = "hostname_A"
        second_hostname = "hostname_B"
        template_content = "!\n${hostname}\n!\n${ %s }\n${ %s }" % (var_1_name, var_2_name)

        p = Project("My Project")
        ct = ConfigTemplate("Template name", project=p, template_content=template_content)

        ct.update_template_variable(var_1_name, var_1_desc)
        ct.update_template_variable(var_2_name, var_2_desc)

        tvs1 = TemplateValueSet(hostname=first_hostname, config_template=ct)
        tvs1.update_variable_value(var_1_name, "first value")
        tvs1.update_variable_value(var_2_name, "second value")
        tvs2 = TemplateValueSet(hostname=second_hostname, config_template=ct)
        tvs2.update_variable_value(var_1_name, "first value")
        tvs2.update_variable_value(var_2_name, "second value")

        db.session.add(p)
        db.session.add(ct)
        db.session.add(tvs1)
        db.session.add(tvs2)
        db.session.commit()

        response = self.client.get(
            url_for("download_all_config_as_zip", project_id=ct.project.id, config_template_id=ct.id)
        )
        self.assert200(response)
        # the content is validated within a functional test case


class CeleryTaskTest(BaseFlaskTest):

    def setUp(self):
        super().setUp()
        # clean FTP and TFTP directories for the test cases
        if os.path.exists(app.config["FTP_DIRECTORY"]):
            shutil.rmtree(os.path.join(app.config["FTP_DIRECTORY"]))
            os.makedirs(app.config["FTP_DIRECTORY"])

        if os.path.exists(app.config["TFTP_DIRECTORY"]):
            shutil.rmtree(os.path.join(app.config["TFTP_DIRECTORY"]))
            os.makedirs(app.config["TFTP_DIRECTORY"])

    def _create_test_data(self):
        # create test data
        template_content = "!\nhostname ${hostname}\n!"
        p = Project(name="project")
        ct = ConfigTemplate(name="template", project=p, template_content=template_content)
        tvs1 = TemplateValueSet(hostname="tvs1", config_template=ct)
        tvs2 = TemplateValueSet(hostname="tvs2", config_template=ct)
        tvs3 = TemplateValueSet(hostname="tvs3", config_template=ct)
        tvs4 = TemplateValueSet(hostname="tvs4", config_template=ct)
        db.session.add_all([p, ct, tvs1, tvs2, tvs3, tvs4])
        db.session.commit()

    def _required_services_running(self):
        # verify celery worker state and redis state
        response = self.client.get(url_for("appliance_status_json"))
        content = json.loads(response.data.decode("utf-8"))

        self.assertTrue("redis" in content.keys())
        self.assertTrue("celery_worker" in content.keys())

        if not content["redis"]:
            self.fail("redis not running")

        if not content["celery_worker"]:
            self.fail("celery worker not running")

    def _get_task_state(self, status_url):
        response = self.client.get(status_url)
        return json.loads(response.data.decode("utf-8"))

    def test_update_local_ftp_config_task(self):
        """
        update ajax call to schedule the update of the configurations on the local FTP directory
        :return:
        """
        self._create_test_data()
        self._required_services_running()
        ct = ConfigTemplate.query.filter(ConfigTemplate.name == "template").first()

        response = self.client.post(
            url_for("update_local_ftp_config_task", config_template_id=ct.id)
        )

        # check task status (should be PENDING)
        status_url = response.headers["Location"]
        task_result = self._get_task_state(status_url)

        self.assertEqual(task_result["state"], "PENDING")
        self.assertEqual(task_result["status"], "Pending...")

        # wait two second (should be enough)
        time.sleep(2)

        # check task status again, now it should finished with a SUCCESS state
        task_result = self._get_task_state(status_url)

        self.assertNotEqual(task_result["state"], "PENDING")
        self.assertEqual(task_result["state"], "SUCCESS")
        self.assertEqual(task_result["status"], "")
        self.assertTrue("data" in task_result.keys())
        self.assertTrue("timestamp" in task_result["data"].keys())
        self.assertTrue("error" not in task_result.keys())

        # verify result on disk
        base_path = os.path.join(app.config["FTP_DIRECTORY"], slugify(ct.project.name), slugify(ct.name))
        self.assertTrue(os.path.exists(base_path), base_path)
        self.assertTrue(os.path.isdir(base_path), base_path)
        for tvs in ct.template_value_sets:
            exp_file = tvs.hostname + "_config.txt"
            self.assertTrue(os.path.exists(os.path.join(base_path, exp_file)))
            self.assertTrue(os.path.isfile(os.path.join(base_path, exp_file)))

        # cleanup
        shutil.rmtree(os.path.join(app.config["FTP_DIRECTORY"], slugify(ct.project.name)))

    def test_update_local_tftp_config_task(self):
        """
        update ajax call to schedule the update of the configurations on the local TFTP directory
        :return:
        """
        self._create_test_data()
        self._required_services_running()
        ct = ConfigTemplate.query.filter(ConfigTemplate.name == "template").first()

        response = self.client.post(
            url_for("update_local_tftp_config_task", config_template_id=ct.id)
        )

        # check task status (should be PENDING)
        status_url = response.headers["Location"]
        task_result = self._get_task_state(status_url)

        self.assertEqual(task_result["state"], "PENDING")
        self.assertEqual(task_result["status"], "Pending...")

        # wait two second (should be enough)
        time.sleep(2)

        # check task status again, now it should finished with a SUCCESS state
        task_result = self._get_task_state(status_url)

        self.assertNotEqual(task_result["state"], "PENDING")
        self.assertEqual(task_result["state"], "SUCCESS")
        self.assertEqual(task_result["status"], "")
        self.assertTrue("data" in task_result.keys())
        self.assertTrue("timestamp" in task_result["data"].keys())
        self.assertTrue("error" not in task_result.keys())

        # verify result on disk
        base_path = os.path.join(app.config["TFTP_DIRECTORY"], slugify(ct.project.name), slugify(ct.name))
        self.assertTrue(os.path.exists(base_path), base_path)
        self.assertTrue(os.path.isdir(base_path), base_path)
        for tvs in ct.template_value_sets:
            exp_file = tvs.hostname + "_config.txt"
            self.assertTrue(os.path.exists(os.path.join(base_path, exp_file)))
            self.assertTrue(os.path.isfile(os.path.join(base_path, exp_file)))

        # cleanup
        shutil.rmtree(os.path.join(app.config["TFTP_DIRECTORY"], slugify(ct.project.name)))
