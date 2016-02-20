"""
Test cases for the export features
"""
import os
import shutil
from app import db, app
from app.models import Project, ConfigTemplate, TemplateValueSet
from app.utils.export import get_appliance_ftp_password, export_configuration_to_local_ftp, \
    export_configuration_to_local_ftp, export_configuration_to_file_system
from tests import BaseFlaskTest


class LocalExportConfigurationTest(BaseFlaskTest):
    """
    test local export function
    """

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

    def test_get_ftp_password(self):
        """
        test the read function of the FTP password
        :return:
        """
        # write test file (normally created during the deployment of the appliance)
        f = open("ftp_user.key", "w+")
        f.write("dummy")
        f.close()

        # get FTP appliance password
        ftp_pwd = get_appliance_ftp_password()
        self.assertEqual(ftp_pwd, "dummy")

    def test_export_configuration_to_local_ftp_with_invalid_value(self):
        """
        test ValueError is no TemplateValueSet is given
        :return:
        """
        with self.assertRaises(ValueError):
            export_configuration_to_local_ftp("Moh")

    def test_export_configuration_to_local_ftp(self):
        """
        export a configuration to the local ftp server
        :return:
        """
        self._create_test_data()
        expected_content = "!\nhostname tvs1\n!"
        expected_file = os.path.join(
            app.config["FTP_DIRECTORY"],
            "project",
            "template",
            "tvs1_config.txt"
        )

        tvs = TemplateValueSet.query.filter_by(hostname="tvs1").first()
        export_configuration_to_local_ftp(tvs)

        # verify result
        self.assertTrue(os.path.exists(expected_file))
        f = open(expected_file)
        file_content = f.read()
        f.close()
        self.assertEqual(expected_content, file_content)

        # cleanup
        shutil.rmtree(os.path.join(app.config["FTP_DIRECTORY"], "project"))

    def test_export_configuration_to_local_tftp(self):
        """
        export a configuration to the local tftp server
        :return:
        """
        self._create_test_data()
        expected_content = "!\nhostname tvs1\n!"
        expected_file = os.path.join(
            app.config["FTP_DIRECTORY"],
            "project",
            "template",
            "tvs1_config.txt"
        )

        tvs = TemplateValueSet.query.filter_by(hostname="tvs1").first()
        export_configuration_to_local_ftp(tvs)

        # verify result
        self.assertTrue(os.path.exists(expected_file))
        f = open(expected_file)
        file_content = f.read()
        f.close()
        self.assertEqual(expected_content, file_content)

        # cleanup
        shutil.rmtree(os.path.join(app.config["FTP_DIRECTORY"], "project"))

    def test_permission_error_export_configuration_to_local_directory(self):
        """
        failed configuration export to a local directory
        :return:
        """
        self._create_test_data()
        tvs = TemplateValueSet.query.filter_by(hostname="tvs1").first()

        with self.assertRaises(PermissionError):
            export_configuration_to_file_system(tvs, "/root")
