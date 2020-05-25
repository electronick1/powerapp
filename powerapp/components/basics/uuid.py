import uuid

from powerapp.core.pipeline.entities import (
    register_pa_entity,
)


@register_pa_entity("GetUUID4Component")
def get_uuid4():
    return str(uuid.uuid4())
