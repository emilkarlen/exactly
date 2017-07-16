from exactly_lib.type_system_values.concrete_string_values import string_value_of_single_string
from exactly_lib.type_system_values.list_value import ListValue


def empty_list_value() -> ListValue:
    return ListValue([])


def list_value_of_string_constants(str_list: list) -> ListValue:
    return ListValue([string_value_of_single_string(s)
                      for s in str_list])
