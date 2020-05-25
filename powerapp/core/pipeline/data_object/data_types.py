from typing import Dict


TRANSOFRMATION_TYPES = {
    "str": str,
    "list": list,
    "dict": dict,
    "int": int,
    "float": float,
}


DATA_TYPES_MAP: Dict[object, object] = {}


def get_powerapp_data_type(obj):
    for obj_type, obj_generate in DATA_TYPES_MAP.items():
        if isinstance(obj, obj_type):
            return obj_generate

    return None


class BaseObjectType:
    # List of methods which user is not able to call, but internally for instance - they
    # will work fine
    __not_allowed__ = [
        "__class__",
        "__delattr__",
        "__dir__",
        "__doc__",
        "__getattribute__",
        "__getattr__",
        "__getnewargs__",
        "__hash__",
        "__init__",
        "__init_subclass__",
        "__new__",
        "__reduce__",
        "__reduce_ex__",
        "__setattr__",
        "__subclasshook__",
        "__module__",
        "__annotations__",
        "__code__",
        "__defaults__",
        "__globals__",
        "__modules__",
        "__self__",
        "__setattr__",
        "__delattr__",
        "__get__",
        "__set__",
        "__copy__",
        "__deepcopy__",
        "__builtin__",
        "__main__",
        "__requires__",
        "__builtins__",
        "__import__",
        "__file__",
        "__subclasses__",
        "__new__",
        "__coerce__",
        "__metaclass__",
        "__bases__",
        "__weakref__",
        "__slots__"
    ]

    def get_attribute(self, name):
        if str(name) in self.__not_allowed__:
            raise RuntimeError("Method not allowed to execute")

        return getattr(self, name)


class StrDataType(BaseObjectType, str):
    __not_allowed__ = BaseObjectType.__not_allowed__ + ["__mul__", "__pow__"]

DATA_TYPES_MAP[str] = StrDataType


class IntDataType(BaseObjectType, int):
    pass

DATA_TYPES_MAP[int] = IntDataType


class ListDataType(BaseObjectType, list):
    __not_allowed__ = BaseObjectType.__not_allowed__ + ["__mul__", "__pow__"]

DATA_TYPES_MAP[list] = ListDataType


class SetDataType(BaseObjectType, set):
    pass

DATA_TYPES_MAP[set] = ListDataType


class DictDataType(BaseObjectType, dict):
    pass

DATA_TYPES_MAP[dict] = DictDataType
