import json
from examples.twist_todoist.app import app

if __name__ == "__main__":
    with open("app.json", "w") as f:
        f.write(json.dumps(app.to_json()))
