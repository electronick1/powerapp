_POWERAPP_ENTITIES = dict()


class PowerAppEntity:
    __entity_code__ = None


def register_pa_entity(default_e_code=None):
    def register(entity):
        if default_e_code:
            entity.__entity_code__ = default_e_code
            e_code = default_e_code
        else:
            e_code = entity.__entity_code__

        if e_code is None:
            raise RuntimeError("Entity code is None")

        if e_code in _POWERAPP_ENTITIES:
            raise RuntimeError("Entity `%s` already exisits" % e_code)

        _POWERAPP_ENTITIES[e_code] = entity

        return entity

    return register


def get_pa_entity(code):
    return _POWERAPP_ENTITIES.get(code, None)
