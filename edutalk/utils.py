import requests
import json
import logging
from functools import wraps

from flask import session, request, redirect, url_for, abort, jsonify, flash
from flask_login import current_user

from edutalk.config import config

log = logging.getLogger('edutalk.utils')

def login_required(f):
    '''
    Ref: http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/#login-required-decorator

    the decorated function will be passed a kwarg: ``user``, an instance of
    models.User
    '''
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('account.auth_redirect_endpoint'))
            
        if not current_user.approved:
            flash('Please wait for administrator\'s approval', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper


def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_teacher and not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def json_err(reason: str, **others):
    x = {'state': 'error', 'reason': reason}
    x.update(others)
    return jsonify(x)


# def flask_login(user):
#     # update http session
#     session['uid'] = user.id
#     return user


def ag_post(data):
    '''
    AG post request worker

    Args:
        data: payload to be attached in the post request.

    Returns:
        res: response from AG.
    '''
    try:
        response = json.loads(
            requests.post(
                config.ag_url+'/ccm_api/',
                json=data
            ).text
        )
        state = (response["state"] == "ok")
        return state, response
    except Exception as err:
        log.exception(err)
        return False, "failed at sending request to AG"
