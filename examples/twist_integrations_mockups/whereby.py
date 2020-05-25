"""
It's just an example of how wereby intergration for Twits from here
https://github.com/Doist/Twist/blob/dev/twist/apps/integrations/core_integrations/whereby/__init__.py

Don't try to run it, it's just a mockup.

Theoratically, all this pipelines can be serialized to json, similar to twist_todoist 
integration example.
"""

from powerapp.core.app.app import PowerApp

from powerapp.components.webhooks.base import Webhooks
from powerapp.components.store.key_value import KeyValueStore

from powerapp.core.pipeline.data_object.data_object import PowerAppObject
from powerapp.components.basics import builtin as pbuiltin

app = PowerApp("Twist_Whereby")


webhooks = Webhooks(app_id=app.id)
user_store = KeyValueStore(app_id=app.id, name="user_ids")


@webhooks.on_event("/integrations/whereby/incoming")
@app.pipeline()
def from_github(p, payload_data: PowerAppObject, headers_payload: PowerAppObject):
    event_type = payload_data["event_type"]
    command_argument = payload_data["command_argument"]
    content = payload_data["content"]
    command = payload_data["command"]

    do_pong = p.s(pbuiltin.dict, {"type": "pong"})
    do_ok = p.s(pbuiltin.dict, {"status": "ok"})
    do_metting = p.s(
        pbuiltin.dict, {"content": make_content(p, command_argument, content, command)}
    )

    p.when(event_type == "ping").do().otherwise(
        p.when(event_type == "uninstall").do(do_ok).otherwise()
    ).result()


def make_content(p, command_argument, content, command):
    whereby_url = p.s(
        pbuiltin.format(command_argument.replace(" ", "_"), "https://whereby.com/%s")
    )

    repl = pbuiltin.format((command_argument, whereby_url), " 📹 [whereby.com: %s](%s)")
    return content.replace(pbuiltin.format((command, command_argument), "%s %s"), repl)
