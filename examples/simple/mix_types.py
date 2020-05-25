from powerapp.core.app.app import PowerApp

from examples.twist_todoist import config

from powerapp.components.basics import builtin as pbuiltin

app = PowerApp("TwistMarketPlace")


@app.pipeline()
def test_int_list(p, data):
    int_value_1 = data["int1"]
    int_value_2 = data["int2"]

    min_value = p.s(pbuiltin.min, int_value_1, int_value_2)

    list_value = data["list"] + [min_value]
    list_value.sort()
    return list_value


test_int_list.compile()
print(test_int_list.run(data={"int1": 100, "int2": 1000, "list": [1, 2, 3]}))
