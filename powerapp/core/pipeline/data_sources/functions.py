from powerapp.core.pipeline.data_object.data_object import PowerAppObject

from powerapp.core.pipeline.data_sources.base import DataPipelineSource


from powerapp.core.pipeline.entities import (
    get_pa_entity,
    register_pa_entity,
)

from powerapp.core.pipeline.pipeline_node import PipelineNode, PipelineRoot

from powerapp.core.pipeline.data_args import (
    kwargs_to_json_recursively,
    kwargs_from_json_recursively,
    execute_kwargs_recursively,
    args_from_json_recursively,
    args_to_json_recursively,
    execute_args_recursively,
)


@register_pa_entity("FunctionDataSource")
class FunctionDataSource(DataPipelineSource):
    def __init__(self, job_to_execute, args=None, kwargs=None):
        self.job_to_execute = job_to_execute
        self.kwargs = kwargs
        self.args = args
        self._pipeline_node = None

    def __call__(self):
        # it's a result
        pa_object = PowerAppObject()
        function_node = PipelineNode(parent=PipelineRoot(None), entity=self)
        PipelineNode(parent=function_node, entity=pa_object)

        return pa_object

    def __set_pipeline_node__(self, pipeline_node):
        self._pipeline_node = pipeline_node

    def __execute__(self, parent_result, pipeline_storage):
        args = execute_args_recursively(self.args, pipeline_storage)
        kwargs = execute_kwargs_recursively(self.kwargs, pipeline_storage)
        return self.job_to_execute(*args, **kwargs)

    def to_json(self):
        return dict(
            __entity_code__=self.__entity_code__,
            job_entity_code=self.job_to_execute.__entity_code__,
            args=args_to_json_recursively(self.args),
            kwargs=kwargs_to_json_recursively(self.kwargs),
        )

    @classmethod
    def from_json(cls, data):
        return cls(
            job_to_execute=get_pa_entity(data["job_entity_code"]),
            args=args_from_json_recursively(data["args"]),
            kwargs=kwargs_from_json_recursively(data["kwargs"]),
        )


@register_pa_entity("InstanceMethodSource")
class InstanceMethodSource(DataPipelineSource):
    def __init__(
        self,
        instance_entity_code,
        instance_kwargs,
        instance_method_name,
        instance_method_kwargs,
    ):
        self.instance_entity_code = instance_entity_code
        self.instance_kwargs = instance_kwargs
        self.instance_method_name = instance_method_name
        self.instance_method_kwargs = instance_method_kwargs

        self._pipeline_node = None

    def __set_pipeline_node__(self, pipeline_node):
        self._pipeline_node = pipeline_node

    def __call__(self):
        # it's a result
        pa_object = PowerAppObject()
        function_node = PipelineNode(parent=PipelineRoot(None), entity=self)
        PipelineNode(parent=function_node, entity=pa_object)

        return pa_object

    def __execute__(self, parent_data, pipeline_storage):
        instance = get_pa_entity(self.instance_entity_code)(**self.instance_kwargs)
        kwargs = execute_kwargs_recursively(
            self.instance_method_kwargs, pipeline_storage
        )
        return getattr(instance, self.instance_method_name)(**kwargs)

    def to_json(self):
        return dict(
            __entity_code__=self.__entity_code__,
            instance_entity_code=self.instance_entity_code,
            instance_kwargs=self.instance_kwargs,
            instance_method_name=self.instance_method_name,
            instance_method_kwargs=kwargs_to_json_recursively(
                self.instance_method_kwargs
            ),
        )

    @classmethod
    def from_json(cls, data):
        return cls(
            instance_entity_code=data["instance_entity_code"],
            instance_kwargs=data["instance_kwargs"],
            instance_method_name=data["instance_method_name"],
            instance_method_kwargs=kwargs_from_json_recursively(
                data["instance_method_kwargs"]
            ),
        )
