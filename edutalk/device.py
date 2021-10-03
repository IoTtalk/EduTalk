from contextlib import suppress
from time import sleep

from flask import jsonify
import logging

from edutalk.models import LectureProject

from edutalk.ag_ccmapi import device
from edutalk.exceptions import CCMAPIError

log = logging.getLogger('edutalk.utils')


def graceful_bind(x: LectureProject, do_id, d_id, user, max_retry=5):
    with suppress(CCMAPIError):
        device.unbind(x.p_id, do_id)  # unbind first

    device.get(x.p_id, do_id)

    for i in range(max_retry):
        try:
            device.bind(x.p_id, do_id, d_id)
            return jsonify({'state': 'ok'})
        except CCMAPIError as e:
            if e.status_code != 404:
                raise

            # mac_addr not found might be caused by race condition
            sleep(1)
            continue

    return jsonify({'state': 'error'}), 400


def unbind(x: LectureProject, do_id, user):
    device.unbind(x.p_id, do_id)
    return jsonify({'state': 'ok'})
