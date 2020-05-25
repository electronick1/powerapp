from powerapp.core.app.app import PowerApp

from powerapp.components.auth.oauth import SimpleOauth
from powerapp.components.webhooks.base import Webhooks
from powerapp.components.store.key_value import KeyValueStore

from examples.twist_todoist import config

app = PowerApp("TwistMarketPlace")

todoist_oauth = SimpleOauth(
    app_id=app.id,
    name="todoist",
    host="https://todoist.com",
    authorization_url="/oauth/authorize/",
    authorization_payload=dict(
        client_id=config.TD_CLIENT_ID,
        scope="data:read_write",
        state=config.STATE,
    ),
    exchange_url="/oauth/access_token/",
)

webhooks = Webhooks(app_id=app.id)
user_store = KeyValueStore(app_id=app.id, name="user_ids")
