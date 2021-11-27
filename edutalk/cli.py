import logging
import os
import shutil
import sys

from argparse import ArgumentParser
from functools import partial

import yaml

# from future import annotations  # test

from edutalk import models
from edutalk.config import config
from edutalk.server import setup_db
from edutalk import ag_ccmapi as ccmapiv0
from edutalk.exceptions import CCMAPIError

log = logging.getLogger('edutalk.cli')


def load_fixtures(fname):
    setup_db()
    db = config.db

    with open(fname) as f, config.app.app_context():
        for x in yaml.load(f):
            if 'model' in x:
                pwd = os.getcwd()
                try:
                    os.chdir(os.path.dirname(fname))
                    load_model(db, x)
                finally:
                    os.chdir(pwd)
            elif 'ccmapi' in x:
                load_ccm_fixture(db, x)

        db.session.commit()


def load_model(db, x):
    model = getattr(models, x['model'])
    tuple(map(lambda r: db.session.add(model(**r)), x['records']))


def load_ccm_fixture(db, x):
    api = x['ccmapi']
    # session = login()
    f = getattr(ccmapiv0, api)
    tuple(map(partial(_get_or_create, f=f), x['records']))


def _get_or_create(r, f):
    """
    Args:
        r: record
        f: function
    """
    try:
        res = f.get(r['name'])
        if "state" in res and res['state'] == 'error':
            raise CCMAPIError
        elif f == ccmapiv0.devicefeature:
            f.update(df_id=res['df_id'],
                     df_name=r['name'],
                     df_type=r['type'],
                     parameter=r['parameter'],
                     comment=res['comment'],
                     df_category=res['df_category'])
    except CCMAPIError:
        f.create(**r)


# def login():
#     username = 'edutalk'
#     password = 'wJyqPHDqHNzEIllKNEJv'
#     with suppress(CCMAPIError):
#         account.create(username, password)
#     _, cookies = account.login(username, password)
#     s = requests.Session()
#     s.cookies.update(cookies)
#     return s


def main():
    parser = ArgumentParser(description='EduTalkcontroller')
    subparsers = parser.add_subparsers(help='available sub-commands')
    parser.add_argument(
        '-c', '--config',
        dest='ini_path',
        default=None,
        help='EduTalk ini config',
    )
    # subcommand: ``initdb``
    # TODO: configurable fixture path, but we do not need it ATM.
    initdb_parser = subparsers.add_parser('initdb', help='initialize database')
    initdb_parser.set_defaults(func=initdb)
    # subcommand: ``start``
    start_parser = subparsers.add_parser('start', help='start server')
    start_parser.set_defaults(func=start)
    # subcommand: ``genconf``
    genconf_parser = subparsers.add_parser(
        'genconf', help='generate sample ini file')
    genconf_parser.add_argument('dest', type=str, help='destination path')
    genconf_parser.set_defaults(func=genconf)

    args = parser.parse_args()
    loadini(args)

    if hasattr(args, 'func'):
        return args.func(args)
    parser.print_help()


def initdb(args):
    p = os.path.join(os.path.dirname(__file__), 'fixtures', 'default.yaml')
    return load_fixtures(p)


def start(args):
    from edutalk.server import main as flask_main
    flask_main()


def loadini(args):
    config.read_config(args.ini_path)


def genconf(args):
    prefixes = [
        os.path.join(sys.prefix, 'share', 'edutalk'),
        os.path.join(os.path.dirname(__file__), '..', 'share'),
    ]
    for prefix in prefixes:
        src = os.path.join(prefix, 'edutalk.ini.sample')
        if os.path.isfile(src):
            break
    else:
        raise OSError('sample ini not found')

    dest = args.dest
    shutil.copy(src, dest)


if __name__ == '__main__':
    main()
