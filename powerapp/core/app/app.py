from powerapp.core.pipeline.pipeline import DataPipeline
from powerapp.core.pipeline.entities import get_pa_entity

from powerapp.core.app.global_store import add_app


class PowerApp:
    def __init__(self, app_token, pipelines=None, oauth_handlers=None, components=None):
        self.id = app_token
        self.pipelines = pipelines or dict()
        self.components = components or []

        add_app(self)

    def pipeline(self):
        def func_wrapper(func):
            data_pipeline = DataPipeline(self.id, pipeline_builder=func)
            self.pipelines[data_pipeline.id] = data_pipeline
            return data_pipeline

        return func_wrapper

    def get_pipeline(self, pipeline_id):
        return self.pipelines[pipeline_id]

    def add_component(self, component):
        self.components.append(component)

    def to_json(self):
        for pipeline in self.pipelines.values():
            pipeline.compile()

        return dict(
            id=self.id,
            pipelines={k: p.to_json() for k, p in self.pipelines.items()},
            components=[c.to_json() for c in self.components],
        )

    @classmethod
    def from_json(cls, data):
        app = cls(
            app_token=data["id"],
            pipelines={
                k: DataPipeline.from_json(data["id"], p)
                for k, p in data["pipelines"].items()
            },
        )

        for component_data in data["components"]:
            component_class = get_pa_entity(component_data["__entity_code__"])
            component_obj = component_class.from_json(app, component_data)
            app.add_component(component_obj)

        return app
