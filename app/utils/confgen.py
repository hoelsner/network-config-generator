"""
Mako based Configuration Generator
"""
import logging
import re

from mako.exceptions import CompileException, SyntaxException
from mako.template import Template

logger = logging.getLogger("confgen")


class TemplateSyntaxException(BaseException):
    """
    This exception is raised, if the rendering of the mako template failed
    """
    pass


class MakoConfigGenerator:
    """
    Config Generator that utilizes the Mako Template Engine
    """

    # variable name regular expression
    _variable_name_regex = r"(\$\{[ ]*(?P<name>[a-zA-Z0-9_]+)[ ]*\})"

    # template content
    _template_string = None
    _template_variable_dict = dict()

    @property
    def template_string(self):
        return self._template_string

    @template_string.setter
    def template_string(self, value):
        self._template_string = value
        # clean list and parse data again
        self._parse_variable_from_template_string()

    @property
    def template_variables(self):
        return sorted(list(self._template_variable_dict.keys()))

    def __init__(self, template_string=""):
        if type(template_string) is not str:
            raise ValueError("template string must be a string type")

        self.template_string = template_string

        self._parse_variable_from_template_string()

    def _parse_variable_from_template_string(self):
        """populates the template_variables list with the variables that are found in the config template

        """
        self._template_variable_dict = dict()
        if self.template_string:
            for var in re.findall(self._variable_name_regex, self.template_string):
                logger.debug("found variable %s" % var[1])
                self.add_variable(var[1])

    def add_variable(self, variable):
        """create a variable with no value

        :param variable:
        :return:
        """
        self.set_variable_value(variable, "")

    def set_variable_value(self, variable, value=""):
        """change the value of the given variable. If the variable doesn't exist, it will be created

        :param variable:
        :param value:
        :return:
        """
        self._template_variable_dict[variable] = value

    def get_variable_value(self, variable):
        """get the value of a variable

        :param variable:
        :return:
        """
        return self._template_variable_dict[variable]

    def get_rendered_result(self, remove_empty_lines=True):
        """render template result

        :param remove_empty_lines: true, if blank lines should be removed
        :return:
        """
        try:
            result = Template(self.template_string).render(**self._template_variable_dict)

        except SyntaxException as ex:
            msg = "Template Syntax error: %s" % str(ex)
            logger.error(msg, exc_info=True)
            raise TemplateSyntaxException(msg)

        except CompileException as ex:
            msg = "Template Compile error: %s" % str(ex)
            logger.error(msg, exc_info=True)
            raise TemplateSyntaxException(msg)

        # remove empty lines
        if remove_empty_lines:
            lines = result.splitlines()
            result = ""
            counter = 1
            for line in lines:
                if line != "":
                    result += line
                    if len(lines) != counter:
                         result += "\n"
                counter += 1

        return result
