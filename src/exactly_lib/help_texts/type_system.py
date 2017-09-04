from exactly_lib.type_system.value_type import ValueType, SymbolValueType, ElementType, LogicValueType

SYMBOL_ELEMENT_TYPE = 'data'
LOGIC_ELEMENT_TYPE = 'logic'

PATH_TYPE = 'path'
STRING_TYPE = 'string'
LIST_TYPE = 'list'

FILE_SELECTOR_TYPE = 'file-selector'
FILE_SELECTOR_VALUE = 'SELECTOR'

LINES_TRANSFORMER_TYPE = 'file-transformer'
LINES_TRANSFORMER_VALUE = 'TRANSFORMER'

PATH_VALUE = 'PATH'
STRING_VALUE = 'STRING'
LIST_VALUE = 'LIST'
LIST_ELEMENT = 'ELEMENT'


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

SYMBOL_TYPE_2_VALUE_TYPE = {
    SymbolValueType.STRING: ValueType.STRING,
    SymbolValueType.PATH: ValueType.PATH,
    SymbolValueType.LIST: ValueType.LIST,
}

SYMBOL_TYPE_LIST_ORDER = [
    SymbolValueType.STRING,
    SymbolValueType.PATH,
    SymbolValueType.LIST,
]

LOGIC_TYPE_INFO_DICT = {
    LogicValueType.FILE_MATCHER: TypeInfo(FILE_SELECTOR_TYPE, FILE_SELECTOR_VALUE),
    LogicValueType.LINES_TRANSFORMER: TypeInfo(LINES_TRANSFORMER_TYPE, LINES_TRANSFORMER_VALUE),
}

LOGIC_TYPE_2_VALUE_TYPE = {
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.LINES_TRANSFORMER: ValueType.LINES_TRANSFORMER,
}

TYPE_INFO_DICT = {
    ValueType.STRING: SYMBOL_TYPE_INFO_DICT[SymbolValueType.STRING],
    ValueType.PATH: SYMBOL_TYPE_INFO_DICT[SymbolValueType.PATH],
    ValueType.LIST: SYMBOL_TYPE_INFO_DICT[SymbolValueType.LIST],

    ValueType.FILE_MATCHER: LOGIC_TYPE_INFO_DICT[LogicValueType.FILE_MATCHER],
    ValueType.LINES_TRANSFORMER: LOGIC_TYPE_INFO_DICT[LogicValueType.LINES_TRANSFORMER],
}

ELEMENT_TYPE_NAME = {
    ElementType.SYMBOL: SYMBOL_ELEMENT_TYPE,
    ElementType.LOGIC: LOGIC_ELEMENT_TYPE,
}


def syntax_of_type_name_in_text(type_name: str) -> str:
    return '"' + type_name + '"'
