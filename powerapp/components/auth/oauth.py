import requests
from urllib.parse import urlencode, urlparse, urljoin

from powerapp.core.apps_supervisor.utils import get_supervisor
from powerapp.core.apps_supervisor.exceptions import Found

from powerapp.components.base import BaseComponent

from powerapp.core.pipeline.entities import (
    register_pa_entity,
)

from powerapp.core.app.global_store import get_app


@register_pa_entity("SimpleOauthComponent")
class SimpleOauth(BaseComponent):
    auth_url = "/oauth/{app_id}/{name}/auth"
    redirect_url = "/oauth/{app_id}/{name}/get_code"

    def __init__(
        self,
        app_id,
        name,
        host,
        authorization_url,
        exchange_url,
        authorization_payload,
        auth_pipeline_id=None,
    ):
        self.app_id = app_id
        self.app = get_app(app_id)
        self.name = name
        self.host = host
        self.authorization_url = authorization_url
        self.authorization_payload = authorization_payload
        self.exchange_url = exchange_url
        self.auth_pipeline_id = auth_pipeline_id

        self.expose_app_urls()
        self.app.add_component(self)

    def expose_app_urls(self):
        auth_url = self.auth_url.format(app_id=self.app.id, name=self.name)
        redirect_url = self.redirect_url.format(app_id=self.app.id, name=self.name)

        if get_supervisor():
            get_supervisor().expose_callback(auth_url, self.on_auth_request)
            get_supervisor().expose_callback(redirect_url, self.on_access_code_request)

    def on_auth_request(self, payload_data, headers_data):
        auth_url_to_redirect = urljoin(
            urljoin(self.host, self.authorization_url),
            "?" + urlencode(self.authorization_payload),
        )
        raise Found(auth_url_to_redirect)

    def on_access_code_request(self, payload_data, headers_data):
        user_id = get_supervisor().auth_callback()
        pipeline_result = self.app.get_pipeline(self.auth_pipeline_id).add_job_or_run(
            user_id=user_id, payload_data=payload_data, headers_data=headers_data
        )
        return "OK"

    def exchange_code(self, exchange_payload):
        exchange_url = urljoin(self.host, self.exchange_url)
        response = requests.post(exchange_url, data=exchange_payload)
        return response.json()

    def api_request(self, api_url, payload):
        api_url = urljoin(self.host, api_url)
        response = requests.post(api_url, data=payload)
        return response.json()

    def authorization_callback(self, pipeline):
        self.auth_pipeline_id = pipeline.id
        return pipeline

    def to_json(self):
        return dict(
            __entity_code__=self.__entity_code__,
            name=self.name,
            host=self.host,
            authorization_url=self.authorization_url,
            authorization_payload=self.authorization_payload,
            exchange_url=self.exchange_url,
            auth_pipeline_id=self.auth_pipeline_id,
        )

    @classmethod
    def from_json(cls, app, data):
        return cls(
            app_id=app.id,
            name=data["name"],
            host=data["host"],
            authorization_url=data["authorization_url"],
            authorization_payload=data["authorization_payload"],
            exchange_url=data["exchange_url"],
            auth_pipeline_id=data["auth_pipeline_id"],
        )
