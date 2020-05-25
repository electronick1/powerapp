import uuid

from examples.twist_todoist.app import app, todoist_oauth, webhooks, user_store
from examples.twist_todoist import config

from powerapp.components.serialization.json import write_json
from powerapp.components.basics.uuid import get_uuid4


@todoist_oauth.authorization_callback
@app.pipeline()
def authorization_pipeline(pipeline, user_id, payload_data):
    access_token = pipeline.source(
        todoist_oauth.exchange_code,
        exchange_payload=dict(
            client_id=config.TD_CLIENT_ID,
            client_secret=config.TD_CLIENT_SECRET,
            code=payload_data["code"],
        ),
    )
    user_access_token = (
        pipeline.when(payload_data["state"] == config.STATE)
        .do(access_token)
        .result()["access_token"]
    )

    store_user_token = pipeline.source(
        user_store.set, key=user_id, value=user_access_token
    )

    return store_user_token


@webhooks.on_event("create_new_task")
@app.pipeline()
def webhook_pipeline(pipeline, payload_data):
    user_id = payload_data["user_id"]
    user_token = pipeline.source(user_store.get, key=user_id)

    task = payload_data["task"]
    task = task.lower().strip().split(":")[0]

    commands_to_execute = pipeline.source(
        write_json,
        [
            {
                "type": "item_add",
                "temp_id": "temp_id",
                "uuid": pipeline.source(get_uuid4),
                "args": {
                    "content": payload_data["task_content"],
                    "project_id": config.TD_PROJECT_ID,
                },
            }
        ],
    )

    request_to_todoist = pipeline.source(
        todoist_oauth.api_request,
        api_url="/sync/v8/sync",
        payload=dict(token=user_token, commands=commands_to_execute),
    )

    return request_to_todoist
