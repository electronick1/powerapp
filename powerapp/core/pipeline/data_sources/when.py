from powerapp.core.utils.ids import make_id
from powerapp.core.pipeline.data_sources.base import DataPipelineSource

from powerapp.core.pipeline.utils import pipeline_storage_cache
from powerapp.core.pipeline.entities import (
    get_pa_entity,
    register_pa_entity,
)

from powerapp.core.pipeline.pipeline_node import (
    PipelineNode,
    PipelineRoot,
    from_json as pipeline_node_from_json,
)
from powerapp.core.pipeline.data_object.data_object import PowerAppObject


@register_pa_entity("WhenStatement")
class WhenStatement(DataPipelineSource):
    def __init__(
        self, statement_node, do_handler_node=None, otherwise_handler_node=None
    ):
        self.statement_node = statement_node
        self.do_handler_node = do_handler_node
        self.otherwise_handler_node = otherwise_handler_node

        self._pipeline_node = None

    def __call__(self):
        # it's a result
        pa_object = PowerAppObject()
        function_node = PipelineNode(parent=PipelineRoot(None), entity=self)
        PipelineNode(parent=function_node, entity=pa_object)

        return pa_object

    def __set_pipeline_node__(self, pipeline_node):
        self._pipeline_node = pipeline_node

    def __execute__(self, parent_data, pipeline_storage):
        its_true = bool(self.statement_node.execute(pipeline_storage))
        if its_true:
            if self.do_handler_node:
                return self.do_handler_node.execute(pipeline_storage)
            else:
                return None

        if self.otherwise_handler_node:
            return self.otherwise_handler_node.execute(pipeline_storage)
        else:
            return None

    def do(self, pa_data_object: PowerAppObject) -> "WhenStatement":
        self.do_handler_node = pa_data_object._pipeline_node
        return self

    def otherwise(self, pa_data_object: PowerAppObject) -> "WhenStatement":
        self.otherwise_handler_node = pa_data_object._pipeline_node
        return self

    def result(self):
        return self()

    def to_json(self):
        do_handler_node = (
            self.do_handler_node.to_json() if self.do_handler_node else None
        )
        otherwise_handler_node = (
            self.otherwise_handler_node.to_json()
            if self.otherwise_handler_node
            else None
        )
        return dict(
            __entity_code__=self.__entity_code__,
            statement_node=self.statement_node.to_json(),
            do_handler_node=do_handler_node,
            otherwise_handler_node=otherwise_handler_node,
        )

    @classmethod
    def from_json(cls, data):
        do_handler = (
            pipeline_node_from_json(data["do_handler_node"])
            if data["do_handler_node"]
            else None
        )
        otherwise_handler = (
            pipeline_node_from_json(data["otherwise_handler_node"])
            if data["otherwise_handler_node"]
            else None
        )
        return cls(
            statement_node=pipeline_node_from_json(data["statement_node"]),
            do_handler_node=do_handler,
            otherwise_handler_node=otherwise_handler,
        )
