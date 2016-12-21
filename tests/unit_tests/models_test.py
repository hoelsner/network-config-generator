"""
test of the model classes that are used within the application
"""
from app.exception import TemplateVariableNotFoundException, TemplateValueNotFoundException
from tests import BaseFlaskTest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Project, ConfigTemplate, TemplateVariable, TemplateValueSet, TemplateValue


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

        ct1 = ConfigTemplate(name="first", project=p1)
        ct2 = ConfigTemplate(name="second", project=p1)

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

        p1ct1 = ConfigTemplate(name="first", project=p1)
        p1ct2 = ConfigTemplate(name="second", project=p1)
        p2ct1 = ConfigTemplate(name="first", template_content=p2ct1_template_content, project=p2)

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
        with self.assertRaises(IntegrityError):
            faulty_ct3 = ConfigTemplate(name="second", template_content="doesn't matter", project=p1)

    def test_config_template_name_validation_function(self):
        p1 = Project(name="Project 1")
        p2 = Project(name="Project 2")
        p1ct1 = ConfigTemplate(name="first", project=p1)
        p2ct2 = ConfigTemplate(name="first", project=p2)
        p1ct3 = ConfigTemplate(name="second", project=p1)
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
        project = Project("Project")
        ct1 = ConfigTemplate(name="First config template", template_content="", project=project)
        ct2 = ConfigTemplate(name="Second config template", template_content="moh", project=project)

        db.session.add(project)
        db.session.add(ct1)
        db.session.add(ct2)
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
        self.assertEqual(repr(filter_ct1), "<ConfigTemplate 'First config template' (1) in Project>")

    def test_config_template_with_large_content(self):
        content_line = "01234566789abcdefghijklmnopqrstuvwxyz"
        test_config_script = ""

        for i in range(1, 100):
            test_config_script += content_line + "\n"

        p = Project(name="project")
        ct = ConfigTemplate(name="large template", template_content=test_config_script, project=p)

        db.session.add(p)
        db.session.add(ct)
        db.session.commit()

        ct_receive = ConfigTemplate.query.filter_by(name="large template").first()

        self.assertEqual(ct_receive.template_content, test_config_script)

    def test_config_template_with_special_characters(self):
        test_config_script = "äöü&%$ß?"
        p = Project("Test project")
        ct = ConfigTemplate(name="template with special characters", template_content=test_config_script, project=p)

        db.session.add(p)
        db.session.add(ct)
        db.session.commit()

        ct_receive = ConfigTemplate.query.filter_by(name="template with special characters").first()

        self.assertEqual(ct_receive.template_content, test_config_script)

    def test_config_template_add_variables_and_lookup(self):
        # create test data
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script", project=p1)
        ct2 = ConfigTemplate(name="second script", project=p1)
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

        # retrieve variables (hostname is automatically created)
        self.assertTrue(len(ct1.variables.all()) == 2+1)
        self.assertTrue(len(ct2.variables.all()) == 1+1)
        self.assertTrue(ct1.is_variable_defined("first_variable"))
        self.assertTrue(ct1.is_variable_defined("second_variable"))
        self.assertTrue(ct2.is_variable_defined("first_variable"))

        ct1var1 = ct1.get_template_variable_by_name("first_variable")
        self.assertTrue(type(ct1var1) is TemplateVariable)
        self.assertEqual(ct1var1.config_template, ct1)
        self.assertEqual(ct1var1.description, ct1var1_desc)

        ct1var2 = ct1.get_template_variable_by_name("second_variable")
        self.assertTrue(type(ct1var2) is TemplateVariable)
        self.assertEqual(ct1var2.config_template, ct1)
        self.assertEqual(ct1var2.description, ct1var2_desc)

        ct2var1 = ct2.get_template_variable_by_name("first_variable")
        self.assertTrue(type(ct2var1) is TemplateVariable)
        self.assertEqual(ct2var1.config_template, ct2)
        self.assertEqual(ct2var1.description, ct2var1_desc)

        # invalid template lookup
        with self.assertRaises(TemplateVariableNotFoundException):
            ct1.get_template_variable_by_name("unknown key")

    def test_config_template_update_variable(self):
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script", project=p1)
        ct2 = ConfigTemplate(name="second script", project=p1)
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

        self.assertTrue(len(ct1.variables.all()) == 2+1)
        self.assertTrue(len(ct2.variables.all()) == 1+1)

        # update value
        ct1var1_desc_mod = "modified description"
        ct1.update_template_variable("first variable", ct1var1_desc_mod)

        ct1var1 = ct1.get_template_variable_by_name("first_variable")
        self.assertNotEqual(ct1var1.description, ct1var1_desc)
        self.assertEqual(ct1var1.description, ct1var1_desc_mod)

    def test_config_template_delete_cascade_option(self):
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script", project=p1)
        ct2 = ConfigTemplate(name="second script", project=p1)
        ct1.project = p1
        ct2.project = p1
        ct1.update_template_variable("test 1")
        ct1.update_template_variable("test 2")
        ct1.update_template_variable("test 3")
        ct2.update_template_variable("other test 1")
        ct2.update_template_variable("other test 2")
        ct2.update_template_variable("other test 3")

        tvs1 = TemplateValueSet("valueset 1", ct1)
        tvs2 = TemplateValueSet("valueset 2", ct1)
        tvs3 = TemplateValueSet("valueset 1", ct2)
        tvs4 = TemplateValueSet("valueset 2", ct2)
        tvs5 = TemplateValueSet("valueset 3", ct2)

        db.session.add_all([p1, ct1, ct2, tvs1, tvs2, tvs3, tvs4, tvs5])
        db.session.commit()

        # test cascade option when deleting objects (hostname is automatically created)
        self.assertTrue(len(TemplateVariable.query.all()) == 6+2, len(TemplateVariable.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 5, len(TemplateValueSet.query.all()))
        db.session.delete(ct1)
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 3+1, len(TemplateVariable.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 3, len(TemplateValueSet.query.all()))
        db.session.delete(ct2)
        self.assertTrue(len(Project.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 0, len(TemplateVariable.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 0, len(TemplateValueSet.query.all()))

    def test_template_value_set_name_validation_function(self):
        p1 = Project(name="Project 1")
        ct1 = ConfigTemplate(name="first script", project=p1)
        ct2 = ConfigTemplate(name="second script", project=p1)

        db.session.add_all([p1, ct1, ct2])
        db.session.commit()

        test_tvs_name = "template value name"
        self.assertTrue(ct1.valid_template_value_set_name(test_tvs_name))

        tvs = TemplateValueSet(test_tvs_name, ct1)
        db.session.add(tvs)
        db.session.commit()

        self.assertFalse(ct1.valid_template_value_set_name(test_tvs_name))
        self.assertTrue(ct2.valid_template_value_set_name(test_tvs_name))

    def test_variable_name_conversion(self):
        p = Project("project")
        ct = ConfigTemplate("My Template", project=p)
        db.session.add_all([p, ct])

        ct.update_template_variable("First Test")
        self.assertTrue(ct.is_variable_defined("First_Test"))

        ct.update_template_variable("first_test")
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(ct.is_variable_defined("first_test"))

        variable_map = (
            ("Value ", "Value"),
            ("the variable name", "the_variable_name"),
            ("%&/__ASDF ", "ASDF"),
        )

        for string, expected_result in variable_map:
            self.assertEqual(ct.convert_variable_name(string), expected_result)

    def test_rename_variable_name_in_config_template(self):
        """
        test rename variable function of the Config Template object and the associated template value set
        :return:
        """
        p = Project("project")
        ct = ConfigTemplate(name="Config Template", project=p)
        ct.update_template_variable("var_1", "first description")
        ct.update_template_variable("var_2", "second description")
        ct.update_template_variable("var_3", "third description")
        tvs = TemplateValueSet("Template", config_template=ct)
        tvs.update_variable_value("var_1", "first value")

        db.session.add_all([p, ct, tvs])
        db.session.commit()

        self.assertTrue(len(ct.variables.all()) == 3+1)
        self.assertTrue(len(tvs.values.all()) == 4)

        with self.assertRaises(TemplateVariableNotFoundException):
            ct.rename_variable(old_name="var1", new_name="var_1_renamed")

        ct.rename_variable(old_name="var_1", new_name="var_1_renamed")

        self.assertTrue(len(ct.variables.all()) == 3+1)
        self.assertTrue(len(tvs.values.all()) == 4)

        self.assertEqual(tvs.get_template_value_by_name_as_string("var_1_renamed"), "first value")

    def test_rename_variable_description_in_config_template(self):
        """
        test change of the description within a Config Template variable
        :return:
        """
        p = Project("project")
        ct = ConfigTemplate(name="Config Template", project=p)
        ct.update_template_variable("var_1", "first description")
        ct.update_template_variable("var_2", "second description")
        ct.update_template_variable("var_3", "third description")
        tvs = TemplateValueSet("Template", config_template=ct)
        tvs.update_variable_value("var_1", "first value")

        db.session.add_all([p, ct, tvs])
        db.session.commit()

        self.assertTrue(len(ct.variables.all()) == 3+1)
        self.assertTrue(len(tvs.values.all()) == 4)

        var_obj = ct.get_template_variable_by_name("var_1")
        var_obj.description = "changed description"
        db.session.add(var_obj)
        db.session.commit()

        self.assertEqual(ct.get_template_variable_by_name("var_1").description, "changed description")


class TemplateVariableDataModelTest(BaseFlaskTest):

    def test_unique_constraint_for_template_variable_name_in_config_template(self):
        var2_name = "var2"
        var2_desc = "another description"
        p = Project("Project")
        ct1 = ConfigTemplate("Test configuration template", project=p)
        var1 = TemplateVariable(ct1, "var1", "description")
        var2 = TemplateVariable(ct1, var2_name, var2_desc)

        db.session.add(p)
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
        received_var2 = TemplateVariable.query.filter_by(var_name_slug=var2_name, config_template=ct1).first()

        self.assertEqual(received_var2, var2)


class TemplateValueSetDataModelTest(BaseFlaskTest):

    def test_create_template_value_set(self):
        p = Project("Project")
        # create first TemplateValueSet
        ct1 = ConfigTemplate("ConfigurationTemplate", project=p)
        tvs1 = TemplateValueSet("ValueSet A", ct1)
        tvs2 = TemplateValueSet("ValueSet B", ct1)

        db.session.add_all([p, ct1, tvs1, tvs2])
        db.session.commit()

        # count results
        self.assertTrue(len(TemplateValueSet.query.all()) == 2)
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)

        # create additional TemplateValueSet
        ct2 = ConfigTemplate("another ConfigurationTemplate", project=p)
        tvs3 = TemplateValueSet("ValueSet A", ct2)
        tvs4 = TemplateValueSet("ValueSet B", ct2)

        db.session.add_all([ct2, tvs3, tvs4])
        db.session.commit()

        # count results
        self.assertTrue(len(TemplateValueSet.query.all()) == 4)
        self.assertTrue(len(ConfigTemplate.query.all()) == 2)

        # verify sample ct1
        received_ct1 = ConfigTemplate.query.filter_by(name="ConfigurationTemplate").first()

        self.assertEqual(received_ct1, ct1)
        self.assertTrue(len(received_ct1.template_value_sets.all()) == 2)
        self.assertEqual(received_ct1.template_value_sets.first(), tvs1)

    def test_template_value_set_name_constraint(self):
        p = Project("project")
        ct1 = ConfigTemplate("Template A", project=p)
        ct2 = ConfigTemplate("Template B", project=p)
        tvs1 = TemplateValueSet("values 1", ct1)
        tvs2 = TemplateValueSet("values 2", ct1)
        tvs3 = TemplateValueSet("values 3", ct2)
        tvs4 = TemplateValueSet("values 4", ct2)

        db.session.add_all([p, ct1, ct2, tvs1, tvs2, tvs3, tvs4])
        db.session.commit()

        self.assertTrue(len(TemplateValueSet.query.all()) == 4)

        # test integrity check
        with self.assertRaises(IntegrityError):
            failed_tvs = TemplateValueSet("values 2", ct1)
        db.session.rollback()

        failed_tvs = TemplateValueSet("values 2")
        failed_tvs.config_template = ct1
        db.session.add(failed_tvs)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        failed_tvs.config_template = ct2

        db.session.add(failed_tvs)
        db.session.commit()

        self.assertTrue(len(TemplateValueSet.query.all()) == 5)

    def test_template_value_set_add_variable_and_lookup(self):
        # create test data
        p = Project(name="project")
        ct = ConfigTemplate(name="template", project=p)
        tvs1 = TemplateValueSet(hostname="tvs1", config_template=ct)
        tvs2 = TemplateValueSet(hostname="tvs2", config_template=ct)
        tvs3 = TemplateValueSet(hostname="tvs3", config_template=ct)
        tvs4 = TemplateValueSet(hostname="tvs4", config_template=ct)
        db.session.add_all([p, ct, tvs1, tvs2, tvs3, tvs4])
        db.session.commit()

        # verify that the variables are not defined
        self.assertFalse(tvs1.is_value_defined("first variable"))
        self.assertFalse(tvs1.is_value_defined("second variable"))
        self.assertFalse(tvs1.is_value_defined("first variable"))

        # add variables to the first configuration template
        tvs1var1_value = "value for first TVS1 variable"
        tvs1var2_value = "value for second TVS1 variable"
        tvs1.update_variable_value("first variable", tvs1var1_value)
        tvs1.update_variable_value("second variable", tvs1var2_value)
        self.assertFalse(tvs2.is_value_defined("first variable"))
        db.session.commit()

        # add variables to the second configuration template
        tvs2var1_value = "value for first TVS2 variable"
        tvs2.update_variable_value("first variable", tvs2var1_value)
        db.session.commit()

        # retrieve variables
        self.assertTrue(len(tvs1.values.all()) == 2+1)
        self.assertTrue(len(tvs2.values.all()) == 1+1)
        self.assertTrue(tvs1.is_value_defined(tvs1.convert_variable_name("first variable")))
        self.assertTrue(tvs1.is_value_defined(tvs1.convert_variable_name("second variable")))
        self.assertTrue(tvs2.is_value_defined(tvs1.convert_variable_name("first variable")))

        tvs1var1 = tvs1.get_template_value_by_name(tvs1.convert_variable_name("first variable"))
        self.assertTrue(type(tvs1var1) is TemplateValue)
        self.assertEqual(tvs1var1.template_value_set, tvs1)
        self.assertEqual(tvs1var1.value, tvs1var1_value)

        tvs1var2 = tvs1.get_template_value_by_name(tvs1.convert_variable_name("second variable"))
        self.assertTrue(type(tvs1var2) is TemplateValue)
        self.assertEqual(tvs1var2.template_value_set, tvs1)
        self.assertEqual(tvs1var2.value, tvs1var2_value)

        tvs2var1 = tvs2.get_template_value_by_name(tvs1.convert_variable_name("first variable"))
        self.assertTrue(type(tvs2var1) is TemplateValue)
        self.assertEqual(tvs2var1.template_value_set, tvs2)
        self.assertEqual(tvs2var1.value, tvs2var1_value)

        # invalid template lookup
        with self.assertRaises(TemplateValueNotFoundException):
            tvs1.get_template_value_by_name("unknown key")

    def test_template_value_set_update_value(self):
        p = Project("Project")
        ct1 = ConfigTemplate(name="first script", project=p)

        tvs1 = TemplateValueSet(hostname="tvs1", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="tvs2", config_template=ct1)

        db.session.add(p)
        db.session.add(ct1)
        db.session.add(tvs1)
        db.session.add(tvs2)
        db.session.commit()

        # verify that the variables are not defined
        self.assertFalse(tvs1.is_value_defined("first variable"))
        self.assertFalse(tvs1.is_value_defined("second variable"))
        self.assertFalse(tvs2.is_value_defined("first variable"))

        # add variables to the first configuration template
        tvs1var1_value = "description for first tvs1 variable"
        tvs1.update_variable_value("first variable", tvs1var1_value)
        tvs1.update_variable_value("second variable", "value for second tvs1 variable")
        tvs2.update_variable_value("first variable", "value for first tvs2 variable")

        self.assertTrue(len(tvs1.values.all()) == 2+1)
        self.assertTrue(len(tvs2.values.all()) == 1+1)

        # update value
        tvs1var1_value_mod = "modified description"
        tvs1.update_variable_value("first variable", tvs1var1_value_mod)

        tvs1var1 = tvs1.get_template_value_by_name("first_variable")
        self.assertNotEqual(tvs1var1.value, tvs1var1_value)
        self.assertEqual(tvs1var1.value, tvs1var1_value_mod)

    def test_template_value_set_delete_cascade_option(self):
        p = Project("project")
        ct1 = ConfigTemplate(name="Config Template", project=p)

        tvs1 = TemplateValueSet(hostname="first script", config_template=ct1)
        tvs2 = TemplateValueSet(hostname="second script", config_template=ct1)

        self.assertEqual(tvs1.update_variable_value("test 1", "value 1"), "test_1")
        self.assertEqual(tvs1.update_variable_value("test 2", "value 2"), "test_2")
        self.assertEqual(tvs1.update_variable_value("test 3", "value 3"), "test_3")
        self.assertEqual(tvs2.update_variable_value("other test 1", "other value 1"), "other_test_1")
        self.assertEqual(tvs2.update_variable_value("other test 2", "other value 2"), "other_test_2")
        self.assertEqual(tvs2.update_variable_value("other test 3", "other value 3"), "other_test_3")

        db.session.add_all([p, tvs1, tvs2, ct1])
        db.session.commit()

        # test cascade option when deleting objects
        self.assertTrue(len(TemplateValue.query.all()) == 6+2, len(TemplateValue.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 2, len(TemplateValueSet.query.all()))
        db.session.delete(tvs1)
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(len(TemplateValue.query.all()) == 4, len(TemplateValue.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 1, len(TemplateValueSet.query.all()))
        db.session.delete(tvs2)
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(len(TemplateValue.query.all()) == 0, len(TemplateValue.query.all()))
        self.assertTrue(len(TemplateValueSet.query.all()) == 0, len(TemplateValueSet.query.all()))

    def test_template_value_set_copy_variable_function_during_creation(self):
        p = Project("project")
        ct = ConfigTemplate(name="my template", template_content="not a real config", project=p)
        self.assertEqual(ct.update_template_variable("var 1"), "var_1")
        self.assertEqual(ct.update_template_variable("var 2"), "var_2")
        self.assertEqual(ct.update_template_variable("var 3"), "var_3")

        db.session.add_all([p, ct])
        db.session.commit()

        # verify database content
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 3+1)

        # create a new template value set and verify that template variables are copied to the TemplateValueSet object
        tvs = TemplateValueSet(hostname="Value Set", config_template=ct)

        self.assertTrue(len(TemplateValue.query.all()) == 4)

        self.assertTrue(tvs.is_value_defined("hostname"))
        self.assertTrue(tvs.is_value_defined("var_1"))
        self.assertTrue(tvs.is_value_defined("var_2"))
        self.assertTrue(tvs.is_value_defined("var_3"))
        var_1_value = "My Value"
        tvs.update_variable_value("var_1", var_1_value)

        # call it again and verify that nothing has changed
        tvs.copy_variables_from_config_template()

        self.assertTrue(len(TemplateValue.query.all()) == 4)

        self.assertTrue(tvs.is_value_defined("hostname"))
        self.assertTrue(tvs.is_value_defined("var_1"))
        self.assertTrue(tvs.is_value_defined("var_2"))
        self.assertTrue(tvs.is_value_defined("var_3"))

        # test that old values are preserved
        self.assertEqual(tvs.get_template_value_by_name_as_string("var_1"), var_1_value)
        self.assertEqual(tvs.get_template_value_by_name_as_string("hostname"), tvs.hostname)

    def test_template_value_set_copy_variable_function_afterwards(self):
        p = Project("project")
        ct = ConfigTemplate(name="my template", template_content="not a real config", project=p)
        ct.update_template_variable("var 1")
        ct.update_template_variable("var 2")
        ct.update_template_variable("var 3")

        db.session.add_all([p, ct])
        db.session.commit()

        # verify database content
        self.assertTrue(len(ConfigTemplate.query.all()) == 1)
        self.assertTrue(len(TemplateVariable.query.all()) == 3+1)

        # create a new template value set without link to a config template
        tvs = TemplateValueSet(hostname="Value Set")

        # define it afterwards (you need to trigger the copy process manually)
        tvs.config_template = ct
        tvs.copy_variables_from_config_template()   # this method will automatically create a 'hostname' variable value

        self.assertTrue(len(TemplateValue.query.all()) == 4)

        self.assertTrue(tvs.is_value_defined("var_1"))
        self.assertTrue(tvs.is_value_defined("var_2"))
        self.assertTrue(tvs.is_value_defined("var_3"))
        self.assertTrue(tvs.is_value_defined("hostname"))

    def test_variable_name_conversion(self):
        p = Project("project")
        ct = ConfigTemplate("config template", project=p)
        tvs = TemplateValueSet("My Template Value set", config_template=ct)

        db.session.add_all([p, ct, tvs])

        tvs.update_variable_value("First Test")
        self.assertTrue(tvs.is_value_defined("First_Test"))

        tvs.update_variable_value("first_test")
        self.assertTrue(len(TemplateValueSet.query.all()) == 1)
        self.assertTrue(tvs.is_value_defined("first_test"))

        variable_map = (
            ("Value ", "Value"),
            ("the variable name", "the_variable_name"),
            ("%&/__ASDF ", "ASDF"),
        )

        for string, expected_result in variable_map:
            self.assertEqual(tvs.convert_variable_name(string), expected_result)


class TemplateValueDataModelTest(BaseFlaskTest):

    def test_unique_constraint_for_template_value_name_in_template_value_set(self):
        var2_name = "var2"
        var2_value = "another value"
        p = Project("project")
        ct = ConfigTemplate("template name", project=p)
        tvs1 = TemplateValueSet("Test configuration template", config_template=ct)
        var1 = TemplateValue(tvs1, "var1", "description")
        var2 = TemplateValue(tvs1, var2_name, var2_value)

        db.session.add(tvs1)
        db.session.add(var1)
        db.session.add(var2)
        db.session.commit()

        # try to add another variable
        var3 = TemplateValue(tvs1, "var2", "with different value")
        db.session.add(var3)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # get same variable and verify description
        received_var2 = TemplateValue.query.filter_by(var_name_slug=var2_name, template_value_set=tvs1).first()

        self.assertEqual(received_var2, var2)
