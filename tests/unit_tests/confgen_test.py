import unittest
from app.utils import MakoConfigGenerator


class MakoConfigGeneratorTest(unittest.TestCase):

    def test_add_template_variable(self):
        dcg = MakoConfigGenerator()
        dcg.add_variable("test")
        self.assertTrue(["test"], dcg.template_variables)

    def test_get_and_set_value_to_variable(self):
        dcg = MakoConfigGenerator()
        dcg.set_variable_value("test")
        dcg.set_variable_value("test2", "value")
        self.assertTrue(["test", "test2"], dcg.template_variables)
        self.assertEqual("", dcg.get_variable_value("test"))
        self.assertEqual("value", dcg.get_variable_value("test2"))

    def test_simple_template_variable_parsing(self):
        test_string = "A simple ${variable} definition"
        expected_result = [
            "variable"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, expected_result)

    def test_parse_multiple_variables_in_single_line(self):
        test_string = "A ${variable} definition with an ${additional} variable"
        expected_result = [
            "variable",
            "additional"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, sorted(expected_result))

    def test_parse_multiple_variables_in_single_line_with_spaces_around(self):
        test_string = "A ${ variable } definition with an ${  additional } variable"
        expected_result = [
            "variable",
            "additional"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, sorted(expected_result))

    def test_parse_variable_at_the_end_of_line(self):
        test_string = "A template at the end of the ${line}"
        expected_result = [
            "line"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, expected_result)

    def test_parse_variable_with_all_possible_characters(self):
        test_string = "long variable ${ 0123456789_abcdefghijklmnopqurstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ } name"
        expected_result = [
            "0123456789_abcdefghijklmnopqurstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, expected_result)

    def test_parse_variable_at_the_beginning_of_line(self):
        test_string = "${variables_definition} at the beginning of the line"
        expected_result = [
            "variables_definition"
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, expected_result)

    def test_invalid_parsing_strings(self):
        """special characters are not allowed within the

        :return:
        """
        test_strings = [
            "${spaces are not allowed within a variable} in a template",
            "${ #### } at the beginning of the line",
            "${ This_%_#_not_+_:_possible } at the beginning of the line",
            "${ this-notation-is-also-not-allowed } at the beginning of the line",
        ]
        dcg = MakoConfigGenerator()

        for tstr in test_strings:
            dcg.template_string = tstr
            self.assertTrue(len(dcg.template_variables) == 0)

    def test_multiline_parsing(self):
        test_string = """Sample ${ config_template } which test
${multiline} parsing
        """
        expected_result = [
            "config_template",
            "multiline",
        ]

        dcg = MakoConfigGenerator(template_string=test_string)

        self.assertListEqual(dcg.template_variables, expected_result)

    def test_render_result(self):
        test_template = "This is ${ var_1 } Sample Template"
        expected_result = "This is a Sample Template"

        dcg = MakoConfigGenerator(template_string=test_template)
        dcg.set_variable_value("var_1", "a")

        self.assertEqual(dcg.get_rendered_result(), expected_result)

    def test_multiline_render_result(self):
        test_template = """
This is ${ var_1 } sample template
with multiline
${ var_2 } in a single string
"""
        # blank lines are removed
        expected_result = "This is a sample template\nwith multiline\nvariables in a single string"

        dcg = MakoConfigGenerator(template_string=test_template)
        dcg.set_variable_value("var_1", "a")
        dcg.set_variable_value("var_2", "variables")

        self.assertEqual(dcg.get_rendered_result(), expected_result)

    def test_line_comment_render_result(self):
        test_template = """
This is ${ var_1 } sample template
## configuration template comment (not rendered)
${ var_2 } in a single string
"""
        # blank lines are removed
        expected_result = "This is a sample template\nvariables in a single string"

        dcg = MakoConfigGenerator(template_string=test_template)
        dcg.set_variable_value("var_1", "a")
        dcg.set_variable_value("var_2", "variables")

        self.assertEqual(dcg.get_rendered_result(), expected_result)

    def test_multiline_comment_render_result(self):
        test_template = """
This is ${ var_1 } sample template
<%doc>
This multiline comment is
not rendered at all
</%doc>
${ var_2 } in a single string
"""
        # blank lines are removed
        expected_result = "This is a sample template\nvariables in a single string"

        dcg = MakoConfigGenerator(template_string=test_template)
        dcg.set_variable_value("var_1", "a")
        dcg.set_variable_value("var_2", "variables")

        self.assertEqual(dcg.get_rendered_result(), expected_result)

    def test_if_else_construct_render_results(self):
        test_template = """! used vars - var_1:${ var_1 } - var_2:${ var_2 }
This is the if-else test
% if var_1:
-> var_1 one is set
% else:
-> var_1 not set
% endif
var_2 is always present: ${ var_2 }"""
        # blank lines are removed
        var_1_not_set_expected_result = "! used vars - var_1: - var_2:value2\nThis is the if-else test\n" \
                                        "-> var_1 not set\nvar_2 is always present: value2"
        var_1_set_expected_result = "! used vars - var_1:value1 - var_2:value2\nThis is the if-else test\n" \
                                    "-> var_1 one is set\nvar_2 is always present: value2"

        dcg = MakoConfigGenerator(template_string=test_template)
        dcg.set_variable_value("var_1", "")
        dcg.set_variable_value("var_2", "value2")
        self.assertEqual(dcg.get_rendered_result(), var_1_not_set_expected_result)

        dcg.set_variable_value("var_1", "value1")
        self.assertEqual(dcg.get_rendered_result(), var_1_set_expected_result)
