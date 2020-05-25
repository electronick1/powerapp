import redis
import json

from powerapp.core.apps_supervisor.message_queues.base import BaseQueue
from powerapp.core.apps_supervisor.utils import get_supervisor


class RedisQueue(BaseQueue):
    def __init__(self, queue_name, redis_kwargs, die_on_error=True):
        self.die_on_error = die_on_error
        self.queue_name = queue_name
        self.redis = redis.Redis(decode_responses=True, **redis_kwargs)

    def add_job(self, app_id, pipeline_id, data):
        self.redis.lpush(
            self.get_queue_key(),
            json.dumps(dict(app_id=app_id, pipeline_id=pipeline_id, data=data)),
        )

    def process(self):
        while True:
            data = self.redis.blpop(self.get_queue_key())[1]

            data = json.loads(data)
            app_id = data["app_id"]
            pipeline_id = data["pipeline_id"]
            pipeline_data = data["data"]

            pipeline = get_supervisor().get_app(app_id).get_pipeline(pipeline_id)

            try:
                pipeline.run(**pipeline_data)
            except Exception as e:
                self.add_job(app_id, pipeline_id, pipeline_data)
                if self.die_on_error:
                    raise
                else:
                    print(e)

    def get_queue_key(self):
        return "powerapp_queue:%s" % self.queue_name
