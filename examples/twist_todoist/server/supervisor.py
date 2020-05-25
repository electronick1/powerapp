import uuid

from flask import Flask, request, redirect

from powerapp.core.apps_supervisor.supervisor import AppsSupervisor
from powerapp.core.apps_supervisor.exceptions import Found
from powerapp.core.apps_supervisor.store.key_value import RedisStore

from powerapp.core.apps_supervisor.message_queues.redis import RedisQueue


flask_app = Flask(__name__)


def expose_callback(url, handler):
    print("EXPOSING URL:", url)

    def wrap_web_handler():
        try:
            return handler(payload_data=dict(request.args), headers_data=dict())

        except Found as e:
            return redirect(e.url, code=302)

    flask_app.route(url, endpoint=str(uuid.uuid4()))(wrap_web_handler)


def auth_callback():
    return 1


apps_supervisor = AppsSupervisor(
    dict(),
    expose_callback=expose_callback,
    auth_callback=auth_callback,
    key_value_store=RedisStore(dict(decode_responses=True)),
    message_queue=RedisQueue("twist_market_place", dict()),
)
