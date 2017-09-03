from exactly_lib.type_system.data import concrete_path_parts
from exactly_lib.type_system.data.path_part import PathPart


def fixed_path_parts(str_or_list) -> PathPart:
    if isinstance(str_or_list, str):
        return concrete_path_parts.PathPartAsFixedPath(str_or_list)
    elif isinstance(str_or_list, list):
        parts = str_or_list
        if not parts:
            return concrete_path_parts.PathPartAsNothing()
        return concrete_path_parts.PathPartAsFixedPath('/'.join(parts))
    else:
        raise TypeError('path parts is neither a str nor a list: ', str(type(str_or_list)))
