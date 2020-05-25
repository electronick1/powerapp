from powerapp.core.pipeline.entities import PowerAppEntity


class DataPipelineSource(PowerAppEntity):
    _pipeline_data = NotImplemented

    def __execute__(self, parent_data, pipeline_storage):
        raise NotImplementedError()
    
    def __set_pipline_node__(self, pipeline_node):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @classmethod
    def from_json(cls, data):
        raise NotImplementedError()
