from threading import local

# TODO: threading.local
local_supervisor = None


def set_supervisor(supervisor):
    global local_supervisor
    local_supervisor = supervisor


def get_supervisor():
    global local_supervisor
    return local_supervisor
