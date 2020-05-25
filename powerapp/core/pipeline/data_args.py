from powerapp.core.pipeline.entities import PowerAppEntity

from powerapp.core.pipeline.entities import get_pa_entity


def execute_args_recursively(args, pipeline_storage):
    if not isinstance(args, (tuple, list)):
        return []

    new_args = []
    for arg in args:
        if isinstance(arg, (tuple, list)):
            new_args.append(execute_args_recursively(arg, pipeline_storage))
        elif isinstance(arg, dict):
            new_args.append(execute_kwargs_recursively(arg, pipeline_storage))
        elif isinstance(arg, PowerAppEntity):
            new_args.append(arg._pipeline_node.execute(pipeline_storage))
        else:
            new_args.append(arg)
    return new_args


def execute_kwargs_recursively(kwargs, pipeline_storage):
    if not isinstance(kwargs, dict):
        return dict()

    new_kwargs = dict()
    for key, value in kwargs.items():
        if isinstance(value, (tuple, list)):
            new_kwargs[key] = execute_args_recursively(value, pipeline_storage)
        elif isinstance(value, dict):
            new_kwargs[key] = execute_kwargs_recursively(value, pipeline_storage)
        elif isinstance(value, PowerAppEntity):
            new_kwargs[key] = value._pipeline_node.execute(pipeline_storage)
        else:
            new_kwargs[key] = value
    return new_kwargs


def args_to_json_recursively(args):
    if not isinstance(args, (tuple, list)):
        return []

    new_args = []
    for arg in args:
        if isinstance(arg, (tuple, list)):
            new_args.append(args_to_json_recursively(arg))
        elif isinstance(arg, dict):
            new_args.append(kwargs_to_json_recursively(arg))
        # TODO: make it by type
        elif hasattr(arg, "_pipeline_node"):
            pipeline_node = arg._pipeline_node.to_json()
            new_args.append(
                {"type": pipeline_node, "__json_type__": "PipelineNodeEntity"}
            )
        elif isinstance(arg, PowerAppEntity):
            new_args.append(arg.to_json())
        else:
            new_args.append(arg)
    return new_args


def kwargs_to_json_recursively(kwargs):
    from powerapp.core.pipeline.data_object.data_object import PowerAppObject

    if not isinstance(kwargs, dict):
        return dict()

    new_kwargs = dict()
    for key, value in kwargs.items():
        if isinstance(value, (tuple, list)):
            new_kwargs[key] = args_to_json_recursively(value)
        elif isinstance(value, dict):
            new_kwargs[key] = kwargs_to_json_recursively(value)
        # TODO: make it by type
        elif hasattr(value, "_pipeline_node"):
            pipeline_node = value._pipeline_node.to_json()
            new_kwargs[key] = {
                "type": pipeline_node,
                "__json_type__": "PipelineNodeEntity",
            }
        elif isinstance(value, PowerAppEntity):
            new_kwargs[key] = value.to_json()
        else:
            new_kwargs[key] = value
    return new_kwargs


def args_from_json_recursively(args):
    from powerapp.core.pipeline.pipeline_node import from_json as node_from_json

    if not isinstance(args, (tuple, list)):
        return []

    new_args = []
    for arg in args:
        if isinstance(arg, (tuple, list)):
            new_args.append(args_from_json_recursively(arg))
        elif isinstance(arg, dict):
            if "__entity_code__" in arg:
                new_args.append(get_pa_entity(arg["__entity_code__"]).from_json(arg))
            elif "__json_type__" in arg:
                if arg["__json_type__"] == "PipelineNodeEntity":
                    pipeline_node = node_from_json(arg["type"])
                    new_args.append(pipeline_node.entity_obj)
                else:
                    raise RuntimeError("Unknown json type")
            else:
                new_args.append(kwargs_from_json_recursively(arg))
        else:
            new_args.append(arg)
    return new_args


def kwargs_from_json_recursively(kwargs):
    from powerapp.core.pipeline.pipeline_node import from_json as node_from_json

    if not isinstance(kwargs, dict):
        return dict()

    new_kwargs = dict()
    for key, value in kwargs.items():
        if isinstance(value, (tuple, list)):
            new_kwargs[key] = args_from_json_recursively(value)
        elif isinstance(value, dict):
            if "__entity_code__" in value:
                new_kwargs[key] = get_pa_entity(value["__entity_code__"]).from_json(
                    value
                )
            elif "__json_type__" in value:
                if value["__json_type__"] == "PipelineNodeEntity":
                    pipeline_node = node_from_json(value["type"])
                    new_kwargs[key] = pipeline_node.entity_obj
                else:
                    raise RuntimeError("Unknown json type")
            else:
                new_kwargs[key] = kwargs_from_json_recursively(value)
        else:
            new_kwargs[key] = value
    return new_kwargs
