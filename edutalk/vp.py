from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import current_user

# from edutalk import device
from edutalk.config import config
from edutalk.models import LectureProject, Lecture, MacAddress
from edutalk.utils import login_required
from edutalk.ag_ccmapi import device
from edutalk.exceptions import CCMAPIError

app = Blueprint('vp', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def index(lec_id):
    lecture = Lecture.query.get(lec_id)
    return render_template('vp/index.html',
                           lecture=Lecture.query.get(lec_id),
                           csm_url=config.csm_url(),
                           dev='{}.{}'.format(current_user.username, lecture.odm))


@app.route('/code', methods=['GET'], strict_slashes=False)
@login_required
def code(lec_id):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    if x is None:
        abort(404)
    return jsonify({'name': x.lecture.da_name, 'code': x.code})


@app.route('/code', methods=['POST'], strict_slashes=False)
@login_required
def code_update(lec_id):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    if x is None:
        abort(404)

    code = request.json.get('code')
    if not code:
        abort(400)

    x.code = code
    db.session.commit()

    return jsonify({'state': 'ok'})


@app.route('/code/reset', methods=['POST'], strict_slashes=False)
@login_required
def code_reset(lec_id):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    if x is None:
        abort(404)

    x.code = lecture.code
    db.session.commit()

    return jsonify({'state': 'ok', 'code': x.code})


@app.route('/code/default', methods=['POST'], strict_slashes=False)
@login_required
def code_default(lec_id):
    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    if x is None:
        abort(404)

    lecture.code = x.code
    db.session.commit()

    return jsonify({'state': 'ok'})


@app.route('/bind/<string:mac_addr>', methods=['POST'], strict_slashes=False)
@login_required
def bind(lec_id, mac_addr):
    # record mac_addr to db
    MacAddress.create(lec_id, mac_addr)

    lecture = Lecture.query.get(lec_id)
    x = LectureProject.get_by_lec_user(lecture, current_user)
    do_id = x.odo['do']['do_id']
    p_id = x.p_id
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
    do_id = x.odo['do']['do_id']
    return device.unbind(x.p_id, do_id)
