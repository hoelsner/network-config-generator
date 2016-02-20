"""
task queue views for the web service (mainly JSON endpoints for AJAX functions)
"""
from flask import jsonify
from app import app, celery
from config import ROOT_URL


@app.route(ROOT_URL + 'task/<task_id>')
def task_status_json(task_id):
    """
    JSON API endpoint to view the state of a task
    :param task_id:
    :return:
    """
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'error' in task.info:
            response['error'] = task.info['error']

        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    # update the response with the result of the task
    response["data"] = task.info
    return jsonify(response)
