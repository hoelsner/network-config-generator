"""
exceptions that are used within the application
"""


class TemplateVariableNotFoundException(BaseException):
    """
    Exception thrown, if a TemplateVariable was not found within a ConfigTemplate
    """
    pass
