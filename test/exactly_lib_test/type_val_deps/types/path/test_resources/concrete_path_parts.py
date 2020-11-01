from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv


def fixed_path_parts(str_or_list) -> PathPartDdv:
    if isinstance(str_or_list, str):
        return path_ddvs.constant_path_part(str_or_list)
    elif isinstance(str_or_list, list):
        parts = str_or_list
        if not parts:
            return path_ddvs.empty_path_part()
        return path_ddvs.constant_path_part('/'.join(parts))
    else:
        raise TypeError('path parts is neither a str nor a list: ', str(type(str_or_list)))
