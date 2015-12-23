"""
exceptions that are used within the application
"""


class TemplateVariableNotFoundException(BaseException):
    """
    Exception thrown, if a TemplateVariable was not found within a ConfigTemplate
    """
    pass


class TemplateValueNotFoundException(BaseException):
    """
    Exception thrown, if a TemplateValue was not found within a TemplateValueSet
    """
    pass
