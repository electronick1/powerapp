from powerapp.core.utils.ids import make_id

from powerapp.core.pipeline.data_object.data_types import (
    DATA_TYPES_MAP,
    TRANSOFRMATION_TYPES,
    BaseObjectType,
)
from powerapp.core.pipeline.utils import pipeline_storage_cache, EXPOSE_METHODS
from powerapp.core.pipeline.entities import (
    PowerAppEntity,
    get_pa_entity,
    register_pa_entity,
)

from powerapp.core.pipeline.data_args import (
    args_to_json_recursively,
    kwargs_to_json_recursively,
    args_from_json_recursively,
    kwargs_from_json_recursively,
    execute_args_recursively,
    execute_kwargs_recursively,
)

1
from powerapp.core.pipeline.pipeline_node import PipelineNode
from powerapp.core.pipeline.data_object.utils import PossibleMagicMethodsToObject


class PowerAppObjectMethod:
    def __init__(self, apply_to_object, method):
        self.apply_to_object = apply_to_object
        self.method = method

    def __call__(self, *args, **kwargs):
        pa_object = PowerAppObject(from_method=self.method, args=args, kwargs=kwargs)
        PipelineNode(parent=self.apply_to_object._pipeline_node, entity=pa_object)
        return pa_object


@register_pa_entity("PowerAppObject")
class PowerAppObject(PowerAppEntity, PossibleMagicMethodsToObject):
    __internal_attrs__ = [
        "__entity_code__",
        "__init__",
        "__execute__",
        "__post_execute__",
        "__set_pipeline_node__",
        "to_json",
        "from_json",
        "_pipeline_node",
        "from_method",
        "args",
        "kwargs",
    ]

    def __init__(
        self, from_method=None, args=None, kwargs=None,
    ):
        self.from_method = from_method

        self.args = args
        self.kwargs = kwargs

        self._pipeline_node = None

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, "__internal_attrs__"):
            return object.__getattribute__(self, name)
        return PowerAppObjectMethod(self, method=name)

    def __set_pipeline_node__(self, pipeline_node):
        self._pipeline_node = pipeline_node

    def __execute__(self, parent_result, pipeline_storage):
        if self.from_method is None:
            return parent_result

        if self.args is None and self.kwargs is None:
            return parent_result

        args = execute_args_recursively(self.args, pipeline_storage)
        kwargs = execute_kwargs_recursively(self.kwargs, pipeline_storage)

        python_type = parent_result.__class__

        if python_type in DATA_TYPES_MAP:
            powerapp_obj = DATA_TYPES_MAP[python_type](parent_result)
            handler = powerapp_obj.get_attribute(self.from_method)
            return self.__post_execute__(handler(*args, **kwargs))
        else:
            raise RuntimeError("Uknown powerapp type: `%s`" % python_type)

    def __post_execute__(self, data):
        return data

    def to_json(self):
        return dict(
            __entity_code__=self.__entity_code__,
            from_method=self.from_method,
            args=args_to_json_recursively(self.args),
            kwargs=kwargs_to_json_recursively(self.kwargs),
        )

    @classmethod
    def from_json(cls, data):
        return cls(
            from_method=data["from_method"],
            args=args_from_json_recursively(data["args"]),
            kwargs=kwargs_from_json_recursively(data["kwargs"]),
        )


@register_pa_entity("PowerAppStrObject")
class PowerAppStrObject(PowerAppObject):
    def __post_execute__(self, data):
        return str(data)


@register_pa_entity("PowerAppListObject")
class PowerAppListObject(PowerAppObject):
    def __post_execute__(self, data):
        return list(data)


@register_pa_entity("PowerAppDictObject")
class PowerAppDictObject(PowerAppObject):
    def __post_execute__(self, data):
        return dict(data)


@register_pa_entity("PowerAppIntObject")
class PowerAppIntObject(PowerAppObject):
    def __post_execute__(self, data):
        return int(data)
