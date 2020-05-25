import inspect


from powerapp.core.pipeline.data_object.data_object import PowerAppObject
from powerapp.core.pipeline.entities import (
    PowerAppEntity,
    get_pa_entity,
)

from powerapp.core.pipeline.data_sources.functions import (
    FunctionDataSource,
    InstanceMethodSource,
)
from powerapp.core.pipeline.data_sources.when import WhenStatement

from powerapp.core.pipeline.pipeline_node import (
    PipelineNode,
    PipelineRoot,
    from_json as pipeline_node_from_json,
)

from powerapp.core.apps_supervisor.utils import get_supervisor
from powerapp.components.message_queue.pipelines import (
    call_pipeline_async,
    map_pipeline_async,
)


class PipelineStorage:
    def __init__(self, pipeline, initial_storage: dict):
        self.pipeline = pipeline
        self._storage = initial_storage

    def set(self, pipeline_node_id, value):
        self._storage[pipeline_node_id] = value

    def get(self, pipeline_node_id):
        return self._storage[pipeline_node_id]

    def has(self, pipeline_node_id):
        return pipeline_node_id in self._storage


class PipelineController:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def source(self, func, *args, **kwargs):
        if hasattr(func, "__self__"):
            instance = func.__self__
            instance_entity_code = instance.get_entity_code()

            if args:
                raise RuntimeError("Args are not support for instance methods")

            if not get_pa_entity(instance_entity_code):
                raise RuntimeError(
                    "Instance `%s` of the method, is not PowerApp component" % instance
                )
            source = InstanceMethodSource(
                instance_entity_code=instance_entity_code,
                instance_kwargs=instance.get_kwargs(),
                instance_method_name=func.__name__,
                instance_method_kwargs=kwargs,
            )
            return source()
        else:
            entity_code = func.__entity_code__
            if not get_pa_entity(entity_code):
                raise RuntimeError(
                    "Function `%s`, is not PowerApp component" % func.__name__
                )
            return FunctionDataSource(func, args, kwargs)()

    def when(self, statement) -> "WhenStatement":
        return WhenStatement(statement._pipeline_node)

    def async_call(self, pipeline, **kwargs):
        return self.source(
            call_pipeline_async,
            app_id=pipeline.app_id,
            pipeline_id=pipeline.id,
            data=kwargs,
        )

    def async_map(self, pipeline, iter_pa_object):
        return self.source(
            map_pipeline_async,
            app_id=pipeline.app_id,
            pipeline_id=pipeline.id,
            iterator=iter_pa_object,
        )

    # Shortcut
    s = source


class DataPipeline(PowerAppEntity):
    def __init__(
        self, app_id, pipeline_id=None, pipeline_builder=None, pipeline_leaves=None,
    ):
        self.app_id = app_id
        self.id = pipeline_id or "%s:%s" % (app_id, pipeline_builder.__name__)

        self.pipeline_builder = pipeline_builder
        self.pipeline_leaves = pipeline_leaves or []

    def compile(self):
        tree = self.pipeline_builder(PipelineController(self), **self.input_objects())
        if isinstance(tree, list):
            self.pipeline_leaves.extend(tree)
        else:
            self.pipeline_leaves.append(tree)

    def add_job_or_run(self, **pipeline_data):
        message_queue = get_supervisor().message_queue
        if message_queue:
            message_queue.add_job(self.app_id, self.id, pipeline_data)
        else:
            return self.run(**pipeline_data)

    def run(self, **pipeline_data):
        # Note: it's important to not depend on pipeline builder in execute, as it's not
        # serialized and set to None, on the server side
        storage = PipelineStorage(self, initial_storage=pipeline_data)

        pipeline_result = []
        for graph_leave in self.pipeline_leaves:
            try:
                pipeline_result.append(graph_leave._pipeline_node.execute(storage))
            except RaiseStopFlag:
                continue

        return pipeline_result

    def input_objects(self):
        info = inspect.getfullargspec(self.pipeline_builder)
        # pop, pipeline object as a first agument
        pipeline_args = info[0]
        pipeline_args.pop(0)
        powerapp_objects = dict()
        for arg in pipeline_args:
            pa_object = PowerAppObject()
            pipeline_node = PipelineNode(parent=PipelineRoot(arg), entity=pa_object)
            powerapp_objects[arg] = pa_object

        return powerapp_objects

    def to_json(self):
        return dict(
            app_id=self.app_id,
            id=self.id,
            pipeline_leaves=[p._pipeline_node.to_json() for p in self.pipeline_leaves],
        )

    @classmethod
    def from_json(cls, app_id, data):
        if app_id != data["app_id"]:
            raise RuntimeError("App id mistmached")

        pipeline_leaves = []
        for p_data in data["pipeline_leaves"]:
            pipeline_node = pipeline_node_from_json(p_data)
            pipeline_leaves.append(pipeline_node.entity_obj)

        return cls(
            app_id=app_id, pipeline_id=data["id"], pipeline_leaves=pipeline_leaves
        )


class RaiseStopFlag(Exception):
    pass
