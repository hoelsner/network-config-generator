from app import celery
import time


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
