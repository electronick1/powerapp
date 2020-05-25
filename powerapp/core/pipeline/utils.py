
EXPOSE_METHODS = [
    "__getitem__",
    "__add__",
    "__sub__",
    "__mul__",
    "__floordiv__",
    "__div__",
    "__truediv__",
    "__mod__",
    "__divmod__",
    "__pow__",
    "__lshift__",
    "__rshift__",
    "__and__",
    "__or__",
    "__xor__",
    "__pos__",
    "__neg__",
    "__abs__",
    "__invert__",
    "__round__",
    "__floor__",
    "__ceil__",
    "__trunc__",
    "__eq__",
    "__cmp__",
    "__ne__",
    "__lt__",
    "__gt__",
    "__le__",
    "__ge__",
    "__index__",
    "__int__",
    "__long__",
]


def pipeline_storage_cache(func):
    def _wrapper(self, pipeline_storage, *args, **kwargs):
        if pipeline_storage.has(self.id):
            return pipeline_storage.get(self.id)
        
        result = func(self, pipeline_storage, *args, **kwargs)

        pipeline_storage.set(self.id, result)
        return result
    return _wrapper
