from exactly_lib.definitions.entity import types


def def_of_string(symbol_name: str) -> str:
    return types.STRING_TYPE_INFO.identifier + ' ' + symbol_name
