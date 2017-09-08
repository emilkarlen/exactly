from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.type_system.value_type import ValueType, SymbolValueType, ElementType, LogicValueType

SYMBOL_ELEMENT_TYPE = 'data'
LOGIC_ELEMENT_TYPE = 'logic'

PATH_TYPE = 'path'
STRING_TYPE = 'string'
LIST_TYPE = 'list'

LINE_MATCHER_TYPE = 'line-matcher'
LINE_MATCHER_VALUE = 'LINE-MATCHER'

FILE_MATCHER_TYPE = 'file-matcher'
FILE_MATCHER_VALUE = 'FILE-MATCHER'

LINES_TRANSFORMER_TYPE = 'file-transformer'
LINES_TRANSFORMER_VALUE = 'TRANSFORMER'

PATH_VALUE = 'PATH'
STRING_VALUE = 'STRING'
LIST_VALUE = 'LIST'
LIST_ELEMENT = 'ELEMENT'


class TypeInfo:
    def __init__(self,
                 type_name: str,
                 value_name: str,
                 concept_info: SingularAndPluralNameAndCrossReferenceId):
        self.type_name = type_name
        self.value_name = value_name
        self.concept_info = concept_info


SYMBOL_TYPE_INFO_DICT = {
    SymbolValueType.STRING: TypeInfo(STRING_TYPE, STRING_VALUE,
                                     types.STRING_CONCEPT_INFO),
    SymbolValueType.PATH: TypeInfo(PATH_TYPE, PATH_VALUE,
                                   types.PATH_CONCEPT_INFO),
    SymbolValueType.LIST: TypeInfo(LIST_TYPE, LIST_VALUE,
                                   types.LIST_CONCEPT_INFO),
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
    LogicValueType.LINE_MATCHER: TypeInfo(LINE_MATCHER_TYPE, LINE_MATCHER_VALUE,
                                          types.LINE_MATCHER_CONCEPT_INFO),
    LogicValueType.FILE_MATCHER: TypeInfo(FILE_MATCHER_TYPE, FILE_MATCHER_VALUE,
                                          types.FILE_MATCHER_CONCEPT_INFO),
    LogicValueType.LINES_TRANSFORMER: TypeInfo(LINES_TRANSFORMER_TYPE, LINES_TRANSFORMER_VALUE,
                                               types.LINES_TRANSFORMER_CONCEPT_INFO),
}

LOGIC_TYPE_2_VALUE_TYPE = {
    LogicValueType.LINE_MATCHER: ValueType.LINE_MATCHER,
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.LINES_TRANSFORMER: ValueType.LINES_TRANSFORMER,
}

TYPE_INFO_DICT = dict([
                          (SYMBOL_TYPE_2_VALUE_TYPE[data_type], SYMBOL_TYPE_INFO_DICT[data_type])
                          for data_type in SymbolValueType
                      ] +
                      [
                          (LOGIC_TYPE_2_VALUE_TYPE[logic_type], LOGIC_TYPE_INFO_DICT[logic_type])
                          for logic_type in LogicValueType
                      ]
                      )

ELEMENT_TYPE_NAME = {
    ElementType.SYMBOL: SYMBOL_ELEMENT_TYPE,
    ElementType.LOGIC: LOGIC_ELEMENT_TYPE,
}


def syntax_of_type_name_in_text(type_name: str) -> str:
    return '"' + type_name + '"'
