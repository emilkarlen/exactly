from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.path_part import PathPart


def fixed_path_parts(str_or_list) -> PathPart:
    if isinstance(str_or_list, str):
        return file_refs.constant_path_part(str_or_list)
    elif isinstance(str_or_list, list):
        parts = str_or_list
        if not parts:
            return file_refs.empty_path_part()
        return file_refs.constant_path_part('/'.join(parts))
    else:
        raise TypeError('path parts is neither a str nor a list: ', str(type(str_or_list)))
