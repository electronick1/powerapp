import inspect
from powerapp.core.pipeline.entities import PowerAppEntity


class BaseComponent(PowerAppEntity):
    __entity_code__ = NotImplemented
    __do_not_serialize__ = []

    def get_entity_code(self):
        return self.__entity_code__

    def get_kwargs(self):
        arguments = inspect.getfullargspec(self.__class__.__init__).args
        if len(arguments) <= 1:
            return dict()

        kwargs_data = dict()
        for arg in arguments[1:]:
            if arg not in self.__do_not_serialize__:
                kwargs_data[arg] = getattr(self, arg)

        return kwargs_data
