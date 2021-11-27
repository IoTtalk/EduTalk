from flask import Blueprint, render_template, abort

from edutalk.config import config
from edutalk.models import Lecture, LectureProject
from edutalk.utils import login_required
from edutalk.ag_ccmapi import devicemodel

app = Blueprint('demo', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def index(user):
    lesson_data = Lecture.list_()

    return render_template("demo.html",
                           user=user,
                           lecture=None,
                           df_list=None,
                           lesson_data=lesson_data,
                           token=user.token)


@app.route('/<int:id_>', methods=['GET'], strict_slashes=False)
@login_required
def refresh(id_, user):
    lec = Lecture.query.get(id_)
    if lec is None:
        abort(404)

    lesson_data = Lecture.list_()
    df_list = tuple(map(    # output device feature list
        lambda x: x.get('df_name'),
        devicemodel.get(lec.odm)['df_list']))
    LectureProject.get_or_create(user, lec)

    return render_template("demo.html",
                           user=user,
                           lecture=lec,
                           df_list=df_list,
                           lesson_data=lesson_data,
                           token=user.token)
