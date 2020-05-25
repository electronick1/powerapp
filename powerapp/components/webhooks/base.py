from powerapp.core.apps_supervisor.utils import get_supervisor

from powerapp.components.base import BaseComponent

from powerapp.core.pipeline.entities import (
    register_pa_entity,
)

from powerapp.core.app.global_store import get_app


@register_pa_entity("WebhooksComponent")
class Webhooks(BaseComponent):
    webhook_url = "/webhook/{app_id}/{url}"

    def __init__(self, app_id, urls_pipelines_map=None):
        self.app_id = app_id
        self.app = get_app(app_id)
        self.urls_pipelines_map = urls_pipelines_map or dict()

        for url, pipeline_id in self.urls_pipelines_map.items():
            self.expose_webhook_url(url, pipeline_id)

        self.app.add_component(self)

    def expose_webhook_url(self, url, pipeline_id):
        webhook_url = self.webhook_url.format(app_id=self.app.id, url=url)

        if get_supervisor():
            get_supervisor().expose_callback(
                webhook_url, self.call_pipeline(pipeline_id)
            )

    def call_pipeline(self, pipeline_id):
        def wrap_pipeline(payload_data, headers_data):
            pipeline_result = self.app.get_pipeline(pipeline_id).add_job_or_run(
                payload_data=payload_data, headers_data=headers_data
            )
            return "OK"

        return wrap_pipeline

    def on_event(self, url):
        def wrapp_pipeline(pipeline):
            self.urls_pipelines_map[url] = pipeline.id
            self.expose_webhook_url(url, pipeline.id)
            return pipeline

        return wrapp_pipeline

    def to_json(self):
        return dict(
            __entity_code__=self.__entity_code__,
            urls_pipelines_map=self.urls_pipelines_map,
        )

    @classmethod
    def from_json(cls, app, data):
        return cls(app_id=app.id, urls_pipelines_map=data["urls_pipelines_map"])
