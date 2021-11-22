import json
import logging
import re

from datetime import datetime, timedelta
from uuid import uuid4

import requests
import pytz

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text, Boolean, String, Enum, DateTime, JSON
from sqlalchemy import asc
from flask_login import UserMixin
from sqlalchemy.schema import DefaultClause

from edutalk.ag_ccmapi import project, deviceobject, devicefeature, networkapplication as na
from edutalk.exceptions import CCMAPIError

from edutalk.config import config

db = config.db
log = logging.getLogger('edutalk.models')

pid_list = [0]
def get_project_info(pid,user):
    return project.get(pid)['odo'][1]['do_id']

def set_pid(pid):
    pid_list.append(pid)
    return 200

def get_pre_pid():
    return pid_list[-1]

class DictMixin:
    def to_dict(self, fields=None):
        if fields is None:
            fields = map(lambda x: x.name, self.__table__.columns)

        return {x: getattr(self, x) for x in fields}


class TimestampMixin():
    # Ref: https://myapollo.com.tw/zh-tw/sqlalchemy-mixin-and-custom-base-classes/
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(pytz.UTC)
    )


class User(db.Model, DictMixin, TimestampMixin, UserMixin):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(255))  # this is a cache stored the result of ccm api query
    approved = Column(Boolean, default=False)
    # iottalk_id = Column(Integer, nullable=False)
    is_superuser = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey('Group.id'), nullable=False)
    lecture_projects = db.relationship('LectureProject', cascade='all,delete',
                                       backref='user')
    _token = Column(String, nullable=False, unique=True, default=lambda: uuid4().hex)  # just a UUID

    @property
    def token(self):  # readonly
        return self._token

    # _cookies = Column(String())  # the iottalk ccm cookies

    # @property
    # def cookies(self):
    #     return json.loads(self._cookies)

    # @cookies.setter
    # def cookies(self, val: dict):
    #     self._cookies = json.dumps(val)

    # cookies = db.synonym('_cookies', descriptor=cookies)

    # @property
    # def ccm_session(self):
    #     s = getattr(self, '__ccm_session', None)  # cache
    #     if not s:
    #         s = self.__ccm_session = requests.Session()
    #         s.cookies.update(self.cookies)
    #     return s

    @property
    def is_teacher(self):
        return self.group.name == 'teacher'

    @property
    def is_admin(self):
        return self.group.name == 'administrator'

    # for OAuth
    sub = Column(String(255), unique=True)
    email = Column(String(255))

    refresh_token = db.relationship(
        'RefreshToken',
        back_populates='user',
        uselist=False,  # For one-to-one relationship, ref: https://tinyurl.com/jemrw6uf
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    access_tokens = db.relationship(
        'AccessToken',
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )


class Group(db.Model):
    __tablename__ = 'Group'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), unique=True)
    users = db.relationship('User', cascade='all,delete', backref='group')

    @classmethod
    def default(cls):
        if len(User.query.all()) == 0:  # assume the first user is admin
            return cls.query.filter_by(name='administrator').first()
        return cls.query.filter_by(name='student').first()


class Lecture(db.Model, DictMixin):
    __tablename__ = 'Lecture'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    idx = Column(Integer, nullable=False)  # lecture orders
    url = Column(Text)  # HackMD url
    idm = Column(String(255))  # the input device model name
    odm = Column(String(255), nullable=False, unique=True)  # the output device model name
    joins = Column(JSON)
    lecture_projects = db.relationship('LectureProject', cascade='all,delete',
                                       backref='lecture')
    code = Column(String)  # the vpython program

    def __init__(self, **kwargs):
        if 'code_path' in kwargs:
            p = kwargs.pop('code_path')
            with open(p) as f:
                kwargs['code'] = f.read()

        return super().__init__(**kwargs)

    @classmethod
    def list_(cls):
        return tuple(map(
            lambda x: x.to_dict(['id', 'name', 'url', 'idm', 'odm']),
            cls.query.order_by(asc(cls.idx)).all()))

    @property
    def da_name(self):  # readonly
        return self.odm

    @classmethod
    def isexist(cls, name):
        return cls.query.filter_by(name=name).first() is not None


class Template(db.Model, DictMixin):
    __tablename__ = 'Template'
    id = Column(Integer, primary_key=True, nullable=False)
    dm = Column(String(255), nullable=False, unique=True)
    code = Column(String)  # the vpython program template

    def __init__(self, **kwargs):
        if 'code_path' in kwargs:
            p = kwargs.pop('code_path')
            with open(p) as f:
                kwargs['code'] = f.read()

        return super().__init__(**kwargs)

    @classmethod
    def isexist(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first() is not None


class LectureProject(db.Model, DictMixin):
    __tablename__ = 'LectureProject'
    id = Column(Integer, primary_key=True, nullable=False)
    u_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    lec_id = Column(Integer, ForeignKey('Lecture.id'), nullable=False)
    p_id = Column(Integer, nullable=False)  # iottalk project id
    code = Column(String)  # the vpython program
    macaddress = db.relationship('MacAddress', cascade='all,delete',
                                       backref='lectureproject')
    # ``user`` is avialable via backref
    # ``lecture`` is avialable via backref

    @classmethod
    def get_or_create(cls, user, lecture):
        x = cls.query.filter(cls.user == user, cls.lecture == lecture).first()
        if not x:
            p_id = project.create(name=lecture.name)
            project.on(p_id)
            x = cls(user=user, lecture=lecture, p_id=p_id, code=lecture.code)
            x.create_na()
            db.session.add(x)
            db.session.commit()
            # TODO: rollback all ccmapi if any exception
        return x

    def create_na(self):  # create device objects
        # create device objects
        # logger_df_id_list = []
        # for idf in self.lecture.joins:
        #     if idf=="Acceleration-I" or idf=="Gyroscope-I" or idf=="Orientation-I" or idf=="Magnetometer-I" or idf=="Humidity-I" or idf=="UV-I" or idf=="Alcohol-I":
        #         logger_odf_name = idf[:-1]+"logger"
        #         logger_df = devicefeature.feature_get_by_name(logger_odf_name)
        #         logger_df_id = logger_df['df_id']
        #         logger_df_id_list.append(logger_df_id)
        ido_id = deviceobject.create(self.p_id, self.lecture.idm)[0]
        odo_id = deviceobject.create(self.p_id, self.lecture.odm)[0]
        # logger_odo_id = deviceobject.create(self.p_id, "FileLogger1")
        for idf, odf, default_value in self.lecture.joins:
            idf = re.sub(r'_', r'-', idf)
            odf = re.sub(r'_', r'-', odf)
            # if idf=="Acceleration-I" or idf=="Gyroscope-I" or idf=="Orientation-I" or idf=="Magnetometer-I" or idf=="Humidity-I" or idf=="UV-I" or idf=="Alcohol-I":
            #     logger_odf = idf[:-2]+"_logger"
            #     na.create(self.p_id, [(ido_id, idf), (odo_id, odf), (logger_odo_id, logger_odf)])
            # else:
            #     na_id = na.create(self.p_id, [(ido_id, idf), (odo_id, odf)])
            na_id = na.create(self.p_id, [(ido_id, idf), (odo_id, odf)])


    # def get_logger_df_name(df_id_list, idf):
    #     if idf=="Acceleration-I" or idf=="Gyroscope-I" or idf=="Orientation-I" or idf=="Magnetometer-I" or idf=="Humidity-I" or idf=="UV-I" or idf=="Alcohol-I":
    #         logger_odf = idf[:-1]+"logger"
    #         logger_df_id = devicefeature.feature_get_by_name(logger_odf)
    #         df_id_list.append(logger_df_id)

    @property
    def ido(self):
        return deviceobject.get(
            self.p_id,
            project.get(self.p_id)['ido'][0]['do_id'])

    @property
    def odo(self):
        return deviceobject.get(
            self.p_id,
            project.get(self.p_id)['odo'][0]['do_id'])

    @classmethod
    def get_by_lec_user(cls, lecture, user):
        return cls.query.filter(cls.lecture == lecture, cls.user == user).first()

    def delete(self):
        try:
            project.delete(self.p_id)
        except CCMAPIError as e:
            log.warning('user %s project %s delete failed',
                        self.user.username, self.p_id)
        db.session.delete(self)
        db.session.commit()


class RefreshToken(db.Model, TimestampMixin):
    id = Column(Integer, primary_key=True)
    token = Column(Text)

    user_id = Column(Integer, ForeignKey('User.id'))

    user = db.relationship('User', back_populates='refresh_token')
    access_tokens = db.relationship(
        'AccessToken',
        back_populates='refresh_token',
        cascade='all, delete-orphan',
        passive_deletes=True
    )


class AccessToken(db.Model, TimestampMixin):
    id = Column(Integer, primary_key=True)
    token = Column(Text)
    expires_at = Column(db.DateTime())

    user_id = Column(Integer, ForeignKey('User.id'))
    refresh_token_id = Column(Integer, ForeignKey('refresh_token.id'))

    user = db.relationship('User', back_populates='access_tokens')
    refresh_token = db.relationship('RefreshToken', back_populates='access_tokens')


class MacAddress(db.Model, DictMixin):
    __tablename__ = 'MacAddress'
    id = Column(Integer, primary_key=True, nullable=False)
    lec_id = Column(Integer, ForeignKey('LectureProject.lec_id'), nullable=False)
    macaddress = Column(String)

    @classmethod
    def create(cls, lec_id, mac_addr):
        x = cls(lec_id=lec_id, macaddress=mac_addr)
        db.session.add(x)
        db.session.commit()
