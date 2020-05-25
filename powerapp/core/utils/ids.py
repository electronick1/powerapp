import uuid

from powerapp.core.apps_supervisor.utils import get_supervisor


def make_id():
    supervisor = get_supervisor()
    if supervisor:
        return supervisor.id_generator()

    return str(uuid.uuid4())[:8]
