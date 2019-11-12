from typing import Sequence

from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string
from exactly_lib.type_system.data.list_ddv import ListDdv


def empty_list_ddv() -> ListDdv:
    return ListDdv.empty()


def list_ddv_of_string_constants(str_list: Sequence[str]) -> ListDdv:
    return ListDdv([string_ddv_of_single_string(s)
                    for s in str_list])
