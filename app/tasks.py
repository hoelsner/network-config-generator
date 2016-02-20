import datetime
import time
import logging
from app import celery, db
from app.models import ConfigTemplate
from app.utils.export import export_configuration_to_local_ftp, export_configuration_to_local_tftp

logger = logging.getLogger("tasks")


@celery.task()
def debug_celery_task(a, b):
    """
    simple debug task to test the celery task queue
    :param a:
    :param b:
    :return:
    """
    time.sleep(2)
    return {
        "result": a + b
    }


@celery.task()
def update_local_ftp_configurations(config_template_id):
    """
    update the local FTP configuration files
    :return:
    """
    # if the result contains a "error" key, the task is failed
    result = {}
    try:
        config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

        for tvs in config_template.template_value_sets:
            export_configuration_to_local_ftp(tvs)

        config_template.last_successful_ftp_export = datetime.datetime.now()
        db.session.commit()
        result["timestamp"] = config_template.last_successful_ftp_export.strftime('%Y/%m/%d %H:%M')

    except Exception as ex:
        logger.error("failed to update local FTP configuration files", exc_info=True)
        result["error"] = str(ex)

    print(result)
    return result


@celery.task()
def update_local_tftp_configurations(config_template_id):
    """
    update the local TFTP configuration files
    :return:
    """
    # if the result contains a "error" key, the task is failed
    result = {}
    try:
        config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

        for tvs in config_template.template_value_sets:
            export_configuration_to_local_tftp(tvs)

        config_template.last_successful_tftp_export = datetime.datetime.now()
        db.session.commit()
        result["timestamp"] = config_template.last_successful_tftp_export.strftime('%Y/%m/%d %H:%M')

    except Exception as ex:
        logger.error("failed to update local TFTP configuration files", exc_info=True)
        result["error"] = str(ex)

    return result
