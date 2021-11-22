import os

from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort

from edutalk.config import config
from edutalk.models import Lecture, User, Group, AccessToken, RefreshToken, User
from edutalk.utils import login_required, teacher_required
from edutalk.oauth2_client import oauth2_client

import datetime
import logging
import pytz
from authlib.integrations.requests_client import OAuth2Session
from flask_login import current_user, login_user, logout_user
from requests import exceptions as requests_exceptions

app = Blueprint('account', __name__)
db = config.db
log = logging.getLogger('edutalk.account')

@app.route('/', strict_slashes=False)
def index():
    '''
    A placeholder for url_for
    '''
    abort(403)


@app.route('/auth', endpoint='auth_redirect_endpoint')
def auth_redirect():
    # url_for ref: https://flask.palletsprojects.com/en/1.1.x/api/#flask.url_for
    # Authlib doc: https://tinyurl.com/4fcyc7ap
    redirect_uri = url_for('account.oauth2_redirect_endpoint', _external=True)

    # Redirect user-agent to the authorization endpoint
    return oauth2_client.iottalk.authorize_redirect(redirect_uri)


@app.route('/auth/callback', endpoint='oauth2_redirect_endpoint')
def oauth2_callback():
    # Check whether the query parameters has one named `code`
    if not request.args.get('code'):
        if current_user.is_authenticated:
            # Redirect user-agent to the index page if a user is already authenticated
            return redirect(url_for('index'))

        redirect_uri = url_for('account.oauth2_redirect_endpoint', _external=True)

        # Redirect user-agent to the authorization endpoint if a user is not authenticated
        return oauth2_client.iottalk.authorize_redirect(redirect_uri)
    
    try:
        # Exchange access token with an authorization code with token endpoint
        #
        # Ref: https://docs.authlib.org/en/stable/client/frameworks.html#id1
        token_response = oauth2_client.iottalk.authorize_access_token()

        # Parse the received ID token
        user_info = oauth2_client.iottalk.parse_id_token(token_response)
    except Exception:
        log.exception('Get access token failed:')
        return render_template('auth_error.html', error='Something is broken...')

    try:
        user_record = db.session.query(User).filter_by(sub=user_info.get('sub')).first()

        if not user_record:
            # Create a new user record if there does not exist an old one
            if Group.default().id == 1: # is admin, approved as default
                approved = True
            else:
                approved = False

            user_record = User(
                sub=user_info.get('sub'),
                username=user_info.get('preferred_username'),
                email=user_info.get('email'),
                group=Group.default(),
                approved = approved
            )
            db.session.add(user_record)

        # Query the refresh token record
        refresh_token_record = \
            db.session.query(RefreshToken).filter_by(user_id=user_record.id).first()

        if not refresh_token_record:
            # Create a new refresh token record if there does not exist an old one
            refresh_token_record = RefreshToken(
                token=token_response.get('refresh_token'),
                user=user_record
            )
            db.session.add(refresh_token_record)
        elif token_response.get('refresh_token'):
            # If there is a refresh token in a token response, it indicates that
            # the old refresh token is expired, so we need to update the old refresh
            # token with a new one.
            refresh_token_record.token = token_response.get('refresh_token')

        # Create a new access token record
        access_token_record = AccessToken(
            token=token_response.get('access_token'),
            expires_at=(
                datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
                + datetime.timedelta(seconds=token_response.get('expires_in', 0))
            ),
            user=user_record,
            refresh_token=refresh_token_record
        )
        db.session.add(access_token_record)

        # Flush all the pending operations to the database so we can get the actual
        # id value.
        db.session.flush()

        # Store the access token ID to session
        session['access_token_id'] = access_token_record.id
        # Login user
        login_user(user_record)
        log.info('User %r log in', current_user.username)
    except Exception as e:
        db.session.rollback()
        log.error(e)
    else:
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/logout', methods=['POST', ], endpoint='logout_endpoint')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    access_token_record = \
        (db.session
            .query(AccessToken)
            .filter_by(id=session.pop('access_token_id', 0))
            .first()
         )

    if not access_token_record:
        return redirect(url_for('index'))

    # Create an OAuth 2.0 client provided Authlib
    #
    # Ref: https://tinyurl.com/2rs2594h (OAuth2Session documentation)
    oauth2_client = OAuth2Session(
        client_id=config.client_id,
        client_secret=config.client_secret,
        revocation_endpoint_auth_method='client_secret_basic'
    )

    try:
        # Revoke the access token
        response = oauth2_client.revoke_token(
            config.revocation_endpoint,
            token=access_token_record.token,
            token_type_hint='access_token'
        )
        response.raise_for_status()
    except requests_exceptions.Timeout:
        log.warning('Revoke an access token failed due to request timeout')
    except requests_exceptions.TooManyRedirects:
        log.warning('Revoke an access token failed due to too many redirects')
    except (requests_exceptions.HTTPError, requests_exceptions.RequestException) as e:
        log.warning('Revoke an access token failed, %s', e)
    finally:
        # Delete the access token record no matter whether access token revocation is
        # success or not
        db.session.delete(access_token_record)
        log.info('User %r log out', current_user.username)
        db.session.commit()

    logout_user()

    return redirect(url_for('index'))


@app.route('/list', strict_slashes=False)
@login_required
@teacher_required
def list_():
    return render_template(
        'user-list.html',
        users=User.query.all(),
        groups=Group.query.all())


@app.route('/<int:uid>', methods=['DELETE'], strict_slashes=False)
@login_required
@teacher_required
def delete(uid):
    target = User.query.get(uid)
    if target is None:
        return 'User id {} not found'.format(uid), 404
    if target.is_teacher:
        return 'Cannot delete teacher account', 403

    # TO FIX: change account maintenance
    # account.delete(session=target.ccm_session)
    db.session.delete(target)
    db.session.commit()
    return jsonify({'state': 'ok'})


@app.route('/<int:uid>/chgrp/<int:gid>', methods=['POST'], strict_slashes=False)
@login_required
@teacher_required
def chgrp(uid, gid):
    target = User.query.get(uid)
    if target is None:
        return 'User id {} not found'.format(uid), 404
    if target.id == current_user.id:
        return 'Cannot change your own group', 403

    g = Group.query.get(gid)
    if g is None:
        return 'Group id {} not found'.format(gid), 404

    target.group = g
    db.session.commit()
    return jsonify({'state': 'ok'})
