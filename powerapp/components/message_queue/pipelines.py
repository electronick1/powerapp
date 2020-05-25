from powerapp.core.pipeline.entities import (
    register_pa_entity,
)
from powerapp.core.app.global_store import get_app


@register_pa_entity("CallPipelineAsyncComponent")
def call_pipeline_async(app_id, pipeline_id, data):
    return get_app(app_id).get_pipeline(pipeline_id).add_job_or_run(**data)


@register_pa_entity("MapPipelineAsyncComponent")
def map_pipeline_async(app_id, pipeline_id, iterator):
    for row in iterator:
        get_app(app_id).get_pipeline(pipeline_id).add_job_or_run(**row)
