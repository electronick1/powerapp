"""
It's just an example of how github intergration for Twits from here
https://github.com/Doist/Twist/blob/dev/twist/apps/integrations/core_integrations/github/__init__.py

Don't try to run it, it's just a mockup.

Theoratically, all this pipelines can be serialized to json, similar to twst_todoist 
integration example.
"""
from powerapp.core.app.app import PowerApp

from powerapp.components.auth.oauth import SimpleOauth
from powerapp.components.webhooks.base import Webhooks
from powerapp.components.store.key_value import KeyValueStore

from powerapp.core.pipeline.data_object.data_object import PowerAppObject
from powerapp.components.basics import builtin as pbuiltin

from powerapp.core.pipeline.pipeline import RaiseStopFlag


app = PowerApp("Twist_Github")

gh_oauth = SimpleOauth(
    app_id=app.id,
    name="github",
    host="https://github.com",
    authorization_url="/oauth/authorize/",
    authorization_payload=dict(
        client_id="GITHUB", scope="data:read_write", state="GITHUB",
    ),
    exchange_url="/oauth/access_token/",
)

webhooks = Webhooks(app_id=app.id)
user_store = KeyValueStore(app_id=app.id, name="user_ids")


@webhooks.on_event("/integrations/github/from_github")
@app.pipeline()
def from_github(
    pipeline, payload_data: PowerAppObject, headers_payload: PowerAppObject
):
    event_type = headers_payload.get("X-GitHub-Event")

    content = (
        pipeline.when(event_type == "pull_request")
        .do(format_pull_request(pipeline, payload_data))
        .result()
    )

    return (
        pipeline.when(content)
        .do(
            pipeline.source(
                gh_oauth.api_request,
                api_url=payload_data["post_data_url"],
                pyaload={"content": content},
            )
        )
        .result()
    )


def format_pull_request(p, payload_data: PowerAppObject):
    action = payload_data.get("action")
    pull_request = payload_data.get("pull_request")

    stop_when = p.when(not action or not pull_request).do(RaiseStopFlag()).result()

    title = pull_request["title"].replace("[", "(").replace("]", ")")
    url = pull_request["html_url"]
    sender = payload_data["sender"]["login"]

    on_opened = p.s(pbuiltin.format((sender, title, url), "➕ %s opened [%s](%s) PR"))
    on_closed = p.s(pbuiltin.format((sender, title, url), "✅ %s closed [%s](%s) PR"))
    on_reopened = p.s(
        pbuiltin.format((sender, title, url), "🌀 %s reopened [%s](%s) PR")
    )

    when_action = (
        p.when(action == "opened")
        .do(on_opened)
        .otherwise(
            p.when(action == "closed")
            .do(on_closed)
            .otherwise(p.when(action == "reopened").do(on_reopened))
            .result()
        )
        .result()
    )

    return when_action
