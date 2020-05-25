import json
import uuid
import redis

from powerapp.core.apps_supervisor.utils import set_supervisor
from powerapp.core.app.app import PowerApp


class AppsSupervisor:
    def __init__(
        self,
        redis_kwargs,
        expose_callback=None,
        auth_callback=None,
        key_value_store=None,
        message_queue=None,
        id_generator=None,
    ):
        self.redis_kwargs = redis_kwargs
        self.apps = dict()
        self.redis_db = redis.Redis(**redis_kwargs)
        self.expose_callback = expose_callback
        self.auth_callback = auth_callback

        self.key_value_store = key_value_store
        self.message_queue = message_queue

        self.id_generator = id_generator or (lambda: str(uuid.uuid4()))

        set_supervisor(self)

    def get_app(self, app_id):
        if app_id not in self.apps:
            raise RuntimeError("App %s not found " % app_id)
        return self.apps[app_id]

    def add_app(self, app):
        self.apps[app.id] = app

    def add_app_from_file(self, file_path):
        with open(file_path, "r") as f:
            app = PowerApp.from_json(json.loads(f.read()))
            self.add_app(app)
            return app

    def add_apps_from_dir(self, dir_path):
        pass

    def process_message_queue(self):
        self.message_queue.process()
