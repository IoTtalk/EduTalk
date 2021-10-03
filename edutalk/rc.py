import logging
import re

from flask import Blueprint, render_template, session, abort, jsonify, request, redirect
from flask_login import login_user

# from edutalk import device
from edutalk.config import config
from edutalk.models import LectureProject, Lecture, User
from edutalk.utils import login_required
from edutalk.ag_ccmapi import device, devicefeature
from edutalk.exceptions import CCMAPIError

from flask_login import current_user

app = Blueprint('rc', __name__)
db = config.db
log = logging.getLogger('edutalk.rc')


@app.route('/', methods=['GET'], strict_slashes=False)
def index(lec_id):
    token = request.args.get('token')
    if not token and 'uid' not in session:  # no token and user doesn't login
        return redirect(url_for('account.login', next=request.path))
    elif not token and 'uid' in session:  # without token, and already login
        user = User.query.get(session.get('uid'))
    elif token:
        user = User.query.filter_by(_token=token).first()
        if user is None:
            return '''<h2>Token invalid</h2>''', 403

        session.clear()
        login_user(user)

    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, user)
    df_list = {re.sub(r'_', r'-', x['df_name']): x for x in x.ido['df_list']}
    for df in df_list:
        df_info = devicefeature.get(df)
        df_list[df]['df_parameter'] = df_info['df_parameter']
    joins = [{
        'idf': re.sub(r'_', r'-', j[0]),
        'odf': re.sub(r'_', r'-', j[1]),
        'min': df_list[re.sub(r'_', r'-', j[0])]['df_parameter'][0]['min'],
        'max': df_list[re.sub(r'_', r'-', j[0])]['df_parameter'][0]['max'],
        'default': j[2],
    } for j in lecture.joins]

    return render_template('rc/index.html',
                           lecture=lecture,
                           joins=joins,
                           idf_list=[[x[0], ['magic']] for x in lecture.joins],
                           csm_url=config.csm_url(),
                           dm_name=lecture.idm,
                           dev='{}.{}'.format(user.username, lecture.idm))


@app.route('/bind/<string:mac_addr>', methods=['POST'], strict_slashes=False)
@login_required
def bind(lec_id, mac_addr):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    p_id = x.p_id
    do_id = x.ido['do']['do_id']
    device_list = device.get(p_id, do_id)
    d = None
    for candidate in device_list:
        if candidate["mac_addr"] == mac_addr:
            d = candidate
            break
    if d is None:
        raise CCMAPIError
    return device.bind(p_id, do_id, d["d_id"])


@app.route('/unbind/', methods=['POST'], strict_slashes=False)
@login_required
def unbind(lec_id):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    do_id = x.ido['do']['do_id']
    return device.unbind(x.p_id, do_id)
