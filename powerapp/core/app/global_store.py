
# TODO: threading.local
apps = dict()

def add_app(app):
    global apps
    apps[app.id] = app

def get_app(app_id):
    global apps
    return apps[app_id]
