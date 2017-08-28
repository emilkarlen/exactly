from exactly_lib.type_system_values.value_type import ValueType, SymbolValueType, ElementType

SYMBOL_ELEMENT_TYPE = 'symbol'

PATH_TYPE = 'path'
STRING_TYPE = 'string'
LIST_TYPE = 'list'

FILE_SELECTOR_TYPE = 'file-selector'

PATH_VALUE = 'PATH'
STRING_VALUE = 'STRING'
LIST_VALUE = 'LIST'
LIST_ELEMENT = 'ELEMENT'

FILE_SELECTOR_VALUE = 'SELECTOR'


class TypeInfo:
    def __init__(self,
                 type_name: str,
                 value_name: str):
        self.type_name = type_name
        self.value_name = value_name


SYMBOL_TYPE_INFO_DICT = {
    SymbolValueType.STRING: TypeInfo(STRING_TYPE, STRING_VALUE),
    SymbolValueType.PATH: TypeInfo(PATH_TYPE, PATH_VALUE),
    SymbolValueType.LIST: TypeInfo(LIST_TYPE, LIST_VALUE),
}

TYPE_INFO_DICT = {
    ValueType.STRING: SYMBOL_TYPE_INFO_DICT[SymbolValueType.STRING],
    ValueType.PATH: SYMBOL_TYPE_INFO_DICT[SymbolValueType.PATH],
    ValueType.LIST: SYMBOL_TYPE_INFO_DICT[SymbolValueType.LIST],
    ValueType.FILE_SELECTOR: TypeInfo(FILE_SELECTOR_TYPE,
                                      FILE_SELECTOR_VALUE),
}

ELEMENT_TYPE_NAME = {
    ElementType.SYMBOL: SYMBOL_ELEMENT_TYPE,
    ElementType.FILE_SELECTOR: FILE_SELECTOR_TYPE,
}


def syntax_of_type_name_in_text(type_name: str) -> str:
    return '"' + type_name + '"'
