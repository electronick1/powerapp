import json

from powerapp.core.pipeline.entities import (
    register_pa_entity,
)


@register_pa_entity("JSONWriteSerializationComponent")
def write_json(data):
    return json.dumps(data)


@register_pa_entity("JSONReadSerializationComponent")
def read_json(data):
    return json.loads(data)
