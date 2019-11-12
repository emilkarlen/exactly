from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_part import PathPartDdv


def fixed_path_parts(str_or_list) -> PathPartDdv:
    if isinstance(str_or_list, str):
        return paths.constant_path_part(str_or_list)
    elif isinstance(str_or_list, list):
        parts = str_or_list
        if not parts:
            return paths.empty_path_part()
        return paths.constant_path_part('/'.join(parts))
    else:
        raise TypeError('path parts is neither a str nor a list: ', str(type(str_or_list)))
