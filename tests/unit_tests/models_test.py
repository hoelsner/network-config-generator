"""
test of the model classes that are used within the application
"""
from app.exception import TemplateVariableNotFoundException
from tests import BaseFlaskTest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Project, ConfigTemplate, TemplateVariable


class ProjectDataModelTest(BaseFlaskTest):

    def test_create_project(self):
        # create test data
        p1 = Project(name="First Test Project")
        p2 = Project(name="Second Test Project")

        # add data to the database
        db.session.add(p1)
        db.session.add(p2)
        self.assertIsNone(p1.id)
        self.assertIsNone(p2.id)

        db.session.commit()
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)

        # read all data from the database
        projects = Project.query.all()
        received_p1 = projects[0]
        received_p2 = projects[1]

        self.assertEqual(p1, received_p1)
        self.assertEqual(p2, received_p2)
        self.assertEqual(p1.id, received_p1.id)
        self.assertEqual(p2.id, received_p2.id)

        # read specific data from the database
        filter_p1 = Project.query.filter_by(name="First Test Project").first()
        self.assertEqual(filter_p1, p1)

        # check common methods
        self.assertEqual(repr(filter_p1), "<Project 'First Test Project'>")

        # config templates should be empty
        self.assertEqual(received_p1.configtemplates.all(), [])
        self.assertEqual(received_p2.configtemplates.all(), [])

    def test_unique_constrain_of_the_project_name(self):
        # create test data
        p1 = Project(name="First Test Project")
        p2_with_same_name = Project(name="First Test Project")

        db.session.add(p1)
        db.session.add(p2_with_same_name)

        # integrity error is thrown if the changes should be commited
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_project_with_multiple_config_templates(self):
        # create test data
        p1 = Project(name="Project with config templates")

        ct1 = ConfigTemplate(name="first")
        ct2 = ConfigTemplate(name="second")

        ct1.project = p1
        ct2.project = p1

        db.session.add(p1)
        db.session.add(ct1)
        db.session.add(ct2)
        db.session.commit()

        # read the project from the database
        received_p1 = Project.query.filter_by(name="Project with config templates").first()

        received_ct1 = received_p1.configtemplates.all()[0]
        received_ct2 = received_p1.configtemplates.all()[1]

        self.assertEqual(p1, received_p1)
        self.assertEqual(ct1, received_ct1)
        self.assertEqual(ct2, received_ct2)

    def test_config_template_name_constraint(self):
        # create test data
        p1_name = "Project with config templates"
        p2_name = "Another Project with config templates"
        p2ct1_template_content = "Code for the second project"
        p1 = Project(name=p1_name)
        p2 = Project(name=p2_name)

        p1ct1 = ConfigTemplate(name="first")
        p1ct2 = ConfigTemplate(name="second")
        p2ct1 = ConfigTemplate(name="first", template_content=p2ct1_template_content)

        p1ct1.project = p1
        p1ct2.project = p1
        p2ct1.project = p2

        db.session.add_all([p1, p2, p1ct1, p1ct2, p2ct1])
        db.session.commit()

        # get project 1 data and verify results
        received_p1 = Project.query.filter_by(name=p1_name).first()
        self.assertEqual(received_p1, p1)

        # verify results
        query_result = received_p1.configtemplates.all()
        self.assertTrue(len(query_result) == 2)

        # get configuration templates for project 1
        query_result = received_p1.configtemplates.filter_by(name="first").all()
        self.assertTrue(len(query_result) == 1, "Too many results received")

        received_p1ct1 = query_result[0]
        self.assertEqual(received_p1ct1, p1ct1)
        self.assertNotEqual(received_p1ct1.template_content, p2ct1_template_content)

        # get project 2 data and verify results
        received_p2 = Project.query.filter_by(name=p2_name).first()
        self.assertEqual(received_p2, p2)

        # verify results
        query_result = received_p2.configtemplates.all()
        self.assertTrue(len(query_result) == 1)

        # get configuration templates for project 2
        query_result = received_p2.configtemplates.filter_by(name="first").all()
        self.assertTrue(len(query_result) == 1, "Too many results received")

        received_p2ct1 = query_result[0]
        self.assertEqual(received_p2ct1, p2ct1)
        self.assertEqual(received_p2ct1.template_content, p2ct1_template_content)

        # try to create another "second" config template
        faulty_ct3 = ConfigTemplate(name="second", template_content="doesn't matter")
        faulty_ct3.project = p1

        db.session.add(faulty_ct3)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_config_template_name_validation_function(self):
        p1 = Project(name="Project 1")
        p2 = Project(name="Project 2")
        p1ct1 = ConfigTemplate(name="first")
        p2ct2 = ConfigTemplate(name="first")
        p1ct3 = ConfigTemplate(name="second")
        p1ct1.project = p1
        p2ct2.project = p2
        p1ct3.project = p1

        db.session.add(p1)
        db.session.add(p1ct1)
        db.session.commit()

        # test validation of the config template name strings
        self.assertFalse(p1.valid_config_template_name("first"))
        self.assertFalse(p1.valid_config_template_name("second"))

        self.assertTrue(p1.valid_config_template_name("first1"))
        self.assertTrue(p2.valid_config_template_name("second"))

    def test_project_delete_cascade_option(self):
        p1 = Project(name="Project 1")
        p2 = Project(name="Project 2")
        p1ct1 = ConfigTemplate(name="first", project=p1)
        p1ct2 = ConfigTemplate(name="second", project=p1)
        p2ct1 = ConfigTemplate(name="first", project=p2)

        db.session.add_all([p1, p2, p1ct1, p1ct2, p2ct1])
        db.session.commit()

        # test sums in DB
        self.assertTrue(len(Project.query.all()) == 2)
        self.assertTrue(len(ConfigTemplate.query.all()) == 3)

        # delete objects
        db.session.delete(p1ct1)
        self.assertTrue(len(Project.query.all()) == 2)
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)

        db.session.delete(p1)
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)

        db.session.delete(p2)
        self.assertTrue(len(Project.query.all()) == 0)
        self.assertTrue(len(ConfigTemplate.query.all()) == 0)


class ConfigTemplateDataModelTest(BaseFlaskTest):

    def test_create_configuration_template(self):
        ct1 = ConfigTemplate(name="First config template", template_content="")
        ct2 = ConfigTemplate(name="Second config template", template_content="moh")

        db.session.add(ct1)
        db.session.add(ct2)
        self.assertIsNone(ct1.id)
        self.assertIsNone(ct2.id)

        db.session.commit()
        self.assertIsNotNone(ct1.id)
        self.assertIsNotNone(ct2.id)

        # read all data from the database
        configtemplates = ConfigTemplate.query.all()
        received_ct1 = configtemplates[0]
        received_ct2 = configtemplates[1]

        self.assertEqual(ct1, received_ct1)
        self.assertEqual(ct2, received_ct2)
        self.assertEqual(ct1.id, received_ct1.id)
        self.assertEqual(ct2.id, received_ct2.id)

        # read specific data from the database
        filter_ct1 = ConfigTemplate.query.filter_by(name="First config template").first()
        self.assertEqual(filter_ct1, ct1)

        # check common methods
        self.assertEqual(repr(filter_ct1), "<ConfigTemplate 'First config template' (1) in None>")

    def test_config_template_with_large_content(self):
        content_line = "01234566789abcdefghijklmnopqrstuvwxyz"
        test_config_script = ""

        for i in range(1, 100):
            test_config_script += content_line + "\n"

        ct = ConfigTemplate(name="large template", template_content=test_config_script)

        db.session.add(ct)
        db.session.commit()

        ct_receive = ConfigTemplate.query.filter_by(name="large template").first()

        self.assertEqual(ct_receive.template_content, test_config_script)

    def test_config_template_with_special_characters(self):
        test_config_script = "äöü&%$ß?"
        ct = ConfigTemplate(name="template with special characters", template_content=test_config_script)

        db.session.add(ct)
        db.session.commit()

        ct_receive = ConfigTemplate.query.filter_by(name="template with special characters").first()

        self.assertEqual(ct_receive.template_content, test_config_script)

    def test_config_template_add_variables_and_lookup(self):
        # create test data
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script")
        ct2 = ConfigTemplate(name="second script")
        ct1.project = p1
        ct2.project = p1
        db.session.add(p1)
        db.session.add(ct1)
        db.session.add(ct2)
        db.session.commit()

        # verify that the variables are not defined
        self.assertFalse(ct1.is_variable_defined("first variable"))
        self.assertFalse(ct1.is_variable_defined("second variable"))
        self.assertFalse(ct2.is_variable_defined("first variable"))

        # add variables to the first configuration template
        ct1var1_desc = "description for first P1 variable"
        ct1var2_desc = "description for second P1 variable"
        ct1.update_template_variable("first variable", ct1var1_desc)
        ct1.update_template_variable("second variable", ct1var2_desc)
        self.assertFalse(ct2.is_variable_defined("first variable"))
        db.session.commit()

        # add variables to the second configuration template
        ct2var1_desc = "description for first P2 variable"
        ct2.update_template_variable("first variable", ct2var1_desc)
        db.session.commit()

        # retrieve variables
        self.assertTrue(len(ct1.variables.all()) == 2)
        self.assertTrue(len(ct2.variables.all()) == 1)
        self.assertTrue(ct1.is_variable_defined("first variable"))
        self.assertTrue(ct1.is_variable_defined("second variable"))
        self.assertTrue(ct2.is_variable_defined("first variable"))

        ct1var1 = ct1.get_template_variable_by_name("first variable")
        self.assertTrue(type(ct1var1) is TemplateVariable)
        self.assertEqual(ct1var1.config_template, ct1)
        self.assertEqual(ct1var1.description, ct1var1_desc)

        ct1var2 = ct1.get_template_variable_by_name("second variable")
        self.assertTrue(type(ct1var2) is TemplateVariable)
        self.assertEqual(ct1var2.config_template, ct1)
        self.assertEqual(ct1var2.description, ct1var2_desc)

        ct2var1 = ct2.get_template_variable_by_name("first variable")
        self.assertTrue(type(ct2var1) is TemplateVariable)
        self.assertEqual(ct2var1.config_template, ct2)
        self.assertEqual(ct2var1.description, ct2var1_desc)

        # invalid template lookup
        with self.assertRaises(TemplateVariableNotFoundException):
            ct1.get_template_variable_by_name("unknown key")

    def test_config_template_update_variable(self):
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script")
        ct2 = ConfigTemplate(name="second script")
        ct1.project = p1
        ct2.project = p1
        db.session.add(p1)
        db.session.add(ct1)
        db.session.add(ct2)
        db.session.commit()

        # verify that the variables are not defined
        self.assertFalse(ct1.is_variable_defined("first variable"))
        self.assertFalse(ct1.is_variable_defined("second variable"))
        self.assertFalse(ct2.is_variable_defined("first variable"))

        # add variables to the first configuration template
        ct1var1_desc = "description for first P1 variable"
        ct1.update_template_variable("first variable", ct1var1_desc)
        ct1.update_template_variable("second variable", "description for second P1 variable")
        ct2.update_template_variable("first variable", "description for first P2 variable")

        self.assertTrue(len(ct1.variables.all()) == 2)
        self.assertTrue(len(ct2.variables.all()) == 1)

        # update value
        ct1var1_desc_mod = "modified description"
        ct1.update_template_variable("first variable", ct1var1_desc_mod)

        ct1var1 = ct1.get_template_variable_by_name("first variable")
        self.assertNotEqual(ct1var1.description, ct1var1_desc)
        self.assertEqual(ct1var1.description, ct1var1_desc_mod)

    def test_config_template_delete_cascade_option(self):
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script")
        ct2 = ConfigTemplate(name="second script")
        ct1.project = p1
        ct2.project = p1
        ct1.update_template_variable("test 1")
        ct1.update_template_variable("test 2")
        ct1.update_template_variable("test 3")
        ct2.update_template_variable("other test 1")
        ct2.update_template_variable("other test 2")
        ct2.update_template_variable("other test 3")
        db.session.add_all([p1, ct1, ct2])
        db.session.commit()

        # test cascade option when deleting objects
        self.assertTrue(len(TemplateVariable.query.all()) == 6, len(TemplateVariable.query.all()))
        db.session.delete(ct1)
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 3, len(TemplateVariable.query.all()))
        db.session.delete(ct2)
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 0, len(TemplateVariable.query.all()))


class TemplateVariableDataModelTest(BaseFlaskTest):

    def test_unique_constraint_for_template_variable_name_in_config_template(self):
        var2_name = "var2"
        var2_desc = "another description"
        ct1 = ConfigTemplate("Test configuration template")
        var1 = TemplateVariable(ct1, "var1", "description")
        var2 = TemplateVariable(ct1, var2_name, var2_desc)

        db.session.add(ct1)
        db.session.add(var1)
        db.session.add(var2)
        db.session.commit()

        # try to add another variable
        var3 = TemplateVariable(ct1, "var2", "with different value")
        db.session.add(var3)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # get same variable and verify description
        received_var2 = TemplateVariable.query.filter_by(var_name=var2_name, config_template=ct1).first()

        self.assertEqual(received_var2, var2)
