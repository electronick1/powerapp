

class BaseQueue:

    def add_job(self, app_id, pipeline_id, data):
        raise NotImplementedError()

    def process(self):
        raise NotImplementedError()