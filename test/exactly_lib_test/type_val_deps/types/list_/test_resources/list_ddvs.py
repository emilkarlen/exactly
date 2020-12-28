from typing import Sequence

from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.string_.strings_ddvs import string_ddv_of_single_string


def empty_list_ddv() -> ListDdv:
    return ListDdv.empty()


def list_ddv_of_string_constants(str_list: Sequence[str]) -> ListDdv:
    return ListDdv([string_ddv_of_single_string(s)
                    for s in str_list])
