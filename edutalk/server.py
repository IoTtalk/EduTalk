import os

from flask import Flask, request, session, render_template
from flask_login import current_user, LoginManager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from libgravatar import Gravatar
from werkzeug.middleware.proxy_fix import ProxyFix

from edutalk.config import config
from edutalk.models import Lecture, User

from edutalk.account import app as account_app
from edutalk.lecture import app as lecture_app
from edutalk.vp import app as vp_app
from edutalk.rc import app as rc_app
from edutalk.demo import app as demo_app
from edutalk.oauth2_client import oauth2_client

app = Flask(__name__)
app.register_blueprint(account_app, url_prefix='/account')
app.register_blueprint(lecture_app, url_prefix='/lecture')
app.register_blueprint(vp_app, url_prefix='/lecture/<int:lec_id>/vp')
app.register_blueprint(rc_app, url_prefix='/lecture/<int:lec_id>/rc')
app.register_blueprint(demo_app, url_prefix='/demo')


@app.route('/')
def index():
    '''
        route for HomePage
    '''
    uid = session.get('uid', -1)
    return render_template('homepage.html',
        new_admin=config.new_admin,
        lesson_data=Lecture.list_())


@app.url_defaults
def static_file_timestamp(endpoint, values):
    '''
    Append a ``_t`` get parameter to all ``url_for('static')``,
    to deal with browser cache.
    '''
    if endpoint != 'static':
        return

    fname = values.get('filename')
    if not fname:
        return

    path = os.path.join(os.path.dirname(__file__), 'static', fname)
    values['_t'] = round(os.path.getmtime(path))


def setup_db():
    if config.db_conf['type'] == 'sqlite':
        db_url = 'sqlite:///{}'.format(
            os.path.join(config.userdir, config.db_conf['url']))
    else:
        db_url = 'mysql+mysqlconnector://{user}:{passwd}@{host}:{port}/{db}'.format(
            user=config.db_conf['user'],
            passwd=config.db_conf['passwd'],
            host=config.db_conf['host'],
            port=config.db_conf['port'],
            db=config.db_conf['url'],
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config.app = app  # this will initialize the db connection
    import edutalk.models  # import the model declaration
    config.db.create_all(app=app)


def main():
    setup_db()
    app.config['SECRET_KEY'] = config.secret_key
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Configure Flask-Login.
    login_manager = LoginManager()
    login_manager.init_app(app)
    oauth2_client.init_app(app)

    # Register OAuth2 Provider information
    oauth2_client.register(
        name='iottalk',
        client_id=config.client_id,
        client_secret=config.client_secret,
        server_metadata_url=config.discovery_endpoint,
        client_kwargs={'scope': 'openid', }
    )

    # Initialize CSRFProtect app
    CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    app.run(
        host=config.bind,
        port=config.http_port,
        threaded=True,
        debug=config.debug,
    )


if __name__ == '__main__':
    main()
