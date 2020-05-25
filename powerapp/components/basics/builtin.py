from functools import wraps
from powerapp.core.pipeline.entities import register_pa_entity


def call_builtin(builtin):
    @wraps(builtin)
    def _wrap_builtin(*args, **kwargs):
        return builtin(*args, **kwargs)

    return _wrap_builtin


abs = register_pa_entity("AbsComponent")(call_builtin(abs))
max = register_pa_entity("MaxComponent")(call_builtin(max))
min = register_pa_entity("MinComponent")(call_builtin(min))
str = register_pa_entity("StrComponent")(call_builtin(str))
int = register_pa_entity("IntComponent")(call_builtin(int))
list = register_pa_entity("ListComponent")(call_builtin(list))
dict = register_pa_entity("DictComponent")(call_builtin(dict))
set = register_pa_entity("SetComponent")(call_builtin(set))
float = register_pa_entity("FloatComponent")(call_builtin(float))
format = register_pa_entity("FormatComponent")(call_builtin(format))
len = register_pa_entity("LenComponent")(call_builtin(len))
