'''
The configuration system.

This module will export a singleton of ``Config`` -- ``config``.
'''
import logging
import os

from configparser import ConfigParser, ExtendedInterpolation
from six import string_types

from flask_sqlalchemy import SQLAlchemy

__all__ = ('config',)

log = logging.getLogger('iottalk.config')


class Config(object):
    '''
    Main configuration here.

    If a property consider as *readonly*, we will use ``property`` decorator
    for it.

    This class is responsible to setup user config dir.
    On Unix, we will have ``$HOME/.edutalk``;
    '''

    __http_port = 7000
    __bind = '0.0.0.0'
    __debug = False
    __db_conf = {
        'type': 'sqlite',  # or `mysql`
        'url': 'edutalk.db',
        'host': 'localhost',
        'port': -1,
        'user': '',
        'passwd': '',
    }
    __ccm_api = 'https://{ccm_domain_name}/api/v0' #change to the domain you use
    __csm_api = 'https://{csm_domain_name}' #change to the domain you use
    __secret_key = 'edutalk_secret_key'
    __client_id = 'your OAuth App ID'
    __client_secret = 'your OAuth App secret'
    __redirect_uri = 'http(s)://domain or IP/account/auth/callback'
    __discovery_endpoint = 'OAuth discover Endpoint'
    __revocation_endpoint = 'OAuth revoke token Endpoint'
    __db = None
    __userdir = ''
    __app = None
    ag_url = 'http://localhost:8080'
    __new_admin = None

    def __init__(self):
        self.setup_userdir()

    @property
    def userdir(self):
        if self.__userdir:
            return self.__userdir

        if os.name.startswith('posix'):
            self.__userdir = os.path.join(os.getcwd(), 'edutalk')
        else:
            raise OSError('Unsupport os type "{}"'.format(os.name))

        return self.__userdir

    @userdir.setter
    def userdir(self, val):
        self.__userdir = val
        self.setup_userdir()

    def setup_userdir(self):
        path = self.userdir

        if os.path.exists(path) and not os.path.isdir(path):
            raise OSError('Path "{}" is not a dir'.format(path))
        elif os.path.exists(path) and os.path.isdir(path):
            return

        os.mkdir(path)

    @property
    def bind(self):
        return self.__bind

    @bind.setter
    def bind(self, val):
        self.__bind = val

    @property
    def http_port(self):
        return self.__http_port

    @http_port.setter
    def http_port(self, val):
        self.__http_port = val

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, val: int):
        self.__debug = val = bool(val)
        # logging
        logging.basicConfig(level=logging.DEBUG if val else logging.INFO)

    @property
    def db(self):
        '''
        :return: The pony orm db instance without db provider binding
        '''
        if self.__db:
            return self.__db

        self.__db = SQLAlchemy()
        return self.__db

    @property
    def db_conf(self):
        '''
        The db cononection configuration.
        Here is the schema::

            {
                'type': str,
                'url': str,
                'host': str,
                'port': int,
                'user': str,
                'passwd': str,
            }

        >>> config.db_conf = {'type': 'answer', 'port': 42}
        >>> assert config.db_conf['type'] == 'answer'
        >>> config.db_conf['port']
        42
        '''
        return self.__db_conf.copy()

    @db_conf.setter
    def db_conf(self, value):
        '''
        :param dict value: the update dictionary

        We accecpt a subset of value with following schema::

            {
                'type': str,
                'url': str,
                'host': str,
                'port': int,
                'user': str,
                'passwd': str,
            }

        :raise ValueError: if we get any invalid key.
        :raise TypeError: if we get wrong type of content.
        '''
        key_set = ('type', 'url', 'host', 'port', 'user', 'passwd')

        for key, val in value.items():
            if key not in key_set:
                raise ValueError('Invalid key: {!r}'.format(key))
            if key != 'port' and not isinstance(val, string_types):
                raise TypeError('{!r} must be a string'.format(key))
            elif key == 'port' and not isinstance(val, int):
                raise TypeError("'port' must be an int")

        self.__db_conf.update(value)

    @property
    def app(self):
        '''
        The Flask app instance
        '''
        return self.__app

    @app.setter
    def app(self, val):
        '''
        Init the database for the app while setting
        '''
        self.__app = val
        self.db.init_app(self.app)

    @property
    def ccm_api(self):
        '''
        IoTtalk CCM API URL
        '''
        return self.__ccm_api

    # @ccm_api.setter
    # def ccm_api(self, val):
        # val = val[:-1] if val.endswith('/') else val
        # self.__ccm_api = ccm_config.api_url = val

    @property
    def csm_api(self):
        return self.__csm_api

    @csm_api.setter
    def csm_api(self, val):
        val = val[:-1] if val.endswith('/') else val
        self.__csm_api = val

    def csm_url(self, path: str = ''):
        url = '{}/{}'.format(self.csm_api, path)
        return url[:-1] if url.endswith('/') else url

    @property
    def secret_key(self):
        '''
        Flask secret key
        '''
        return self.__secret_key

    @secret_key.setter
    def secret_key(self, val):
        self.__secret_key = val

    @property
    def client_id(self):
        '''
        OAuth 2.0 Client ID
        '''
        return self.__client_id

    @client_id.setter
    def client_id(self, val):
        self.__client_id = val

    @property
    def client_secret(self):
        '''
        OAuth 2.0 Client Secret
        '''
        return self.__client_secret

    @client_secret.setter
    def client_secret(self, val):
        self.__client_secret = val

    @property
    def redirect_uri(self):
        '''
        OAuth 2.0 Redirect URI
        '''
        return self.__redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val):
        self.__redirect_uri = val

    @property
    def discovery_endpoint(self):
        '''
        OpenID Connect Discovery Endpoint
        '''
        return self.__discovery_endpoint

    @discovery_endpoint.setter
    def discovery_endpoint(self, val):
        self.__discovery_endpoint = val

    @property
    def revocation_endpoint(self):
        '''
        OAuth 2.0 revocation endpoint
        '''
        return self.__revocation_endpoint

    @revocation_endpoint.setter
    def revocation_endpoint(self, val):
        self.__revocation_endpoint = val

    @property
    def new_admin(self):
        '''
        The user who is changed to the admin
        '''
        return self.__new_admin

    @new_admin.setter
    def new_admin(self, val):
        self.__new_admin = val

    def read_config(self, path):
        if not path:
            return

        c = ConfigParser(interpolation=ExtendedInterpolation())
        c.read(path)

        def set_(obj, c: 'config section', name, parse: 'function' = str):
            try:
                if isinstance(obj, dict):
                    opt = obj[name]
                    obj[name] = parse(c.get(name, opt))
                else:
                    opt = getattr(obj, name)
                    setattr(self, name, parse(c.get(name, opt)))

            except (AttributeError, KeyError):
                log.warning('Skip unknown config `{}`'.format(name))

        if 'edutalk' in c:  # `edutalk` section
            s = c['edutalk']
            set_(self, s, 'debug', int)
            set_(self, s, 'bind')
            set_(self, s, 'userdir')
            set_(self, s, 'http_port', int)
            set_(self, s, 'secret_key')
            set_(self, s, 'client_id')
            set_(self, s, 'client_secret')
            set_(self, s, 'redirect_uri')
            set_(self, s, 'discovery_endpoint')
            set_(self, s, 'revocation_endpoint')
            set_(self, s, 'admin_username')
            set_(self, s, 'admin_sub')
            set_(self, s, 'admin_email')

        if 'edutalk-db' in c:
            s = c['edutalk-db']
            set_(self.__db_conf, s, 'type')
            set_(self.__db_conf, s, 'url')
            set_(self.__db_conf, s, 'host')
            set_(self.__db_conf, s, 'port', int)
            set_(self.__db_conf, s, 'user')
            set_(self.__db_conf, s, 'passwd')

        if 'iottalk' in c:
            s = c['iottalk']
            set_(self, s, 'csm_api')
            set_(self, s, 'ccm_api')


config = Config()
