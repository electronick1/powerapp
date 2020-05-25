import requests
import flask
from urllib.parse import urlencode, urlparse, urljoin

from powerapp.core.apps_supervisor.utils import get_supervisor
from powerapp.core.apps_supervisor.exceptions import Found

from powerapp.components.base import BaseComponent

from powerapp.core.pipeline.entities import (
    get_pa_entity,
    register_pa_entity,
)

from powerapp.core.app.global_store import get_app


@register_pa_entity("KeyValueStoreComponent")
class KeyValueStore(BaseComponent):
    def __init__(
        self, app_id, name,
    ):
        self.app_id = app_id
        self.app = get_app(app_id)
        self.name = name

        self.app.add_component(self)

    def get(self, key):
        return get_supervisor().key_value_store.get(self.app.id, self.name, key)

    def set(self, key, value):
        return get_supervisor().key_value_store.set(self.app.id, self.name, key, value)

    def to_json(self):
        return dict(__entity_code__=self.__entity_code__, name=self.name,)

    @classmethod
    def from_json(cls, app, data):
        return cls(app_id=app.id, name=data["name"])
