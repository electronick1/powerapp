from powerapp.core.utils.ids import make_id
from typing import Dict

from powerapp.core.pipeline.entities import get_pa_entity
from powerapp.core.pipeline.data_object.data_types import DATA_TYPES_MAP

NODES_TYPES: Dict[str, object] = dict()


def from_json(data):
    parent_class = NODES_TYPES.get(data["node_type"])
    return parent_class.from_json(data)


class PipelineNode:
    node_type = "node"

    def __init__(self, parent, entity, component_id=None):
        self.parent = parent
        self.id = component_id or make_id()
        self.entity_obj = entity

        self.set_self_for_entity()

    def set_self_for_entity(self):
        if hasattr(self.entity_obj, "__set_pipeline_node__"):
            self.entity_obj.__set_pipeline_node__(self)

    def execute(self, pipeline_storage):
        if pipeline_storage.has(self.id):
            return pipeline_storage.get(self.id)

        result = self.parent.execute(pipeline_storage)

        if result is not None:
            if result.__class__ not in DATA_TYPES_MAP:
                raise RuntimeError("TYPE OF OBJECT NOT ALLOWED")

        result = self.entity_obj.__execute__(result, pipeline_storage)

        pipeline_storage.set(self.id, result)
        return result

    def to_json(self):
        return dict(
            node_type=self.node_type,
            id=self.id,
            parent=self.parent.to_json(),
            entity_obj=self.entity_obj.to_json(),
        )

    @classmethod
    def from_json(cls, data):
        entity_code = data["entity_obj"]["__entity_code__"]
        entity_class = get_pa_entity(entity_code)
        entity_obj = entity_class.from_json(data["entity_obj"])

        return cls(
            parent=from_json(data["parent"]), entity=entity_obj, component_id=data["id"]
        )


NODES_TYPES["node"] = PipelineNode


class PipelineRoot:
    node_type = "root"

    def __init__(self, storage_object_id, component_id=None):
        self.id = component_id or make_id()
        self.storage_object_id = storage_object_id

    def execute(self, pipeline_storage):
        if self.storage_object_id is None:
            return None
        return pipeline_storage.get(self.storage_object_id)

    def to_json(self):
        return dict(
            node_type=self.node_type,
            id=self.id,
            storage_object_id=self.storage_object_id,
        )

    @classmethod
    def from_json(cls, data):
        return cls(storage_object_id=data["storage_object_id"], component_id=data["id"])


NODES_TYPES["root"] = PipelineRoot
