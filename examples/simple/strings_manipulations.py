from powerapp.core.app.app import PowerApp

from examples.twist_todoist import config


app = PowerApp("TwistMarketPlace")


@app.pipeline()
def test_strings(p, data):
    return data["string"].lower().strip().split(data["split_by"]) + ["Test Passed"]


test_strings.compile()

print(test_strings.run(data={"string": "QWEQWEQWE", "split_by": "q"}))

