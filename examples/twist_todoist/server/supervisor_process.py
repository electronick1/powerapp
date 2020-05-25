from examples.twist_todoist.server import supervisor

supervisor.apps_supervisor.add_app_from_file("app.json")
supervisor.apps_supervisor.process_message_queue()
