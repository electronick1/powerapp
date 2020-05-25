from examples.twist_todoist.server.supervisor import apps_supervisor, flask_app


app = apps_supervisor.add_app_from_file("app.json")
flask_app.run()
