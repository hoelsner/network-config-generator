"""
export utility functions
"""
import logging
import os

from app.models import TemplateValueSet
from app import app

logger = logging.getLogger("confgen")


def get_appliance_ftp_password():
    """
    get the appliance FTP password
    :return:
    """
    try:
        f = open("ftp_user.key", "r")
        pwd = f.read()
        f.close()
        return pwd

    except:
        logger.error("FTP password not set", exec_info=True)
        return "(not defined)"


def export_configuration_to_file_system(template_value_set, root_folder):
    """
    export a configuration from a template value set to the root directory with the following
    structure

        `/<project_name>/<config_template_name>/<hostname>_config.txt`

    :param template_value_set:
    :param root_folder:
    :return:
    """
    if type(template_value_set) is not TemplateValueSet:
        raise ValueError

    project_dir = template_value_set.config_template.project.name_slug
    template_directory = template_value_set.config_template.name_slug
    file_name = template_value_set.hostname + "_config.txt"

    dest_dir = os.path.join(root_folder, project_dir, template_directory)
    logger.info("export configuration file to: %s/%s" % (dest_dir, file_name))

    # check that the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    f = open(os.path.join(dest_dir, file_name), "w+")
    f.write(template_value_set.get_configuration_result())
    f.close()


def export_configuration_to_local_ftp(template_value_set):
    """
    export configuration to the local FTP directory using the following pattern:

        `/<project_name>/<config_template_name>/<hostname>_config.txt`

    where slugs are used for the `project_name` and the `config_template_name` value

    :param template_value_set:
    :return:
    """
    if type(template_value_set) is not TemplateValueSet:
        raise ValueError

    export_configuration_to_file_system(template_value_set, app.config["FTP_DIRECTORY"])


def export_configuration_to_local_tftp(template_value_set):
    """
    export configuration to the local TFTP directory using the following pattern:

        `/<project_name>/<config_template_name>/<hostname>_config.txt`

    where slugs are used for the `project_name` and the `config_template_name` value

    :param template_value_set:
    :return:
    """
    if type(template_value_set) is not TemplateValueSet:
        raise ValueError

    export_configuration_to_file_system(template_value_set, app.config["TFTP_DIRECTORY"])
