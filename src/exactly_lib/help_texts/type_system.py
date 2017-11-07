from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType

DATA_TYPE_CATEGORY = 'data'
LOGIC_TYPE_CATEGORY = 'logic'

PATH_TYPE = 'path'
STRING_TYPE = 'string'
LIST_TYPE = 'list'

LINE_MATCHER_TYPE = 'line-matcher'
LINE_MATCHER_VALUE = 'LINE-MATCHER'

FILE_MATCHER_TYPE = 'file-matcher'
FILE_MATCHER_VALUE = 'FILE-MATCHER'

LINES_TRANSFORMER_TYPE = 'file-transformer'
LINES_TRANSFORMER_VALUE = 'FILE-TRANSFORMER'

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


DATA_TYPE_INFO_DICT = {
    DataValueType.STRING: TypeInfo(STRING_TYPE, STRING_VALUE,
                                   types.STRING_CONCEPT_INFO),
    DataValueType.PATH: TypeInfo(PATH_TYPE, PATH_VALUE,
                                 types.PATH_CONCEPT_INFO),
    DataValueType.LIST: TypeInfo(LIST_TYPE, LIST_VALUE,
                                 types.LIST_CONCEPT_INFO),
}

DATA_TYPE_2_VALUE_TYPE = {
    DataValueType.STRING: ValueType.STRING,
    DataValueType.PATH: ValueType.PATH,
    DataValueType.LIST: ValueType.LIST,
}

DATA_TYPE_LIST_ORDER = [
    DataValueType.STRING,
    DataValueType.PATH,
    DataValueType.LIST,
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
                          (DATA_TYPE_2_VALUE_TYPE[data_type], DATA_TYPE_INFO_DICT[data_type])
                          for data_type in DataValueType
                      ] +
                      [
                          (LOGIC_TYPE_2_VALUE_TYPE[logic_type], LOGIC_TYPE_INFO_DICT[logic_type])
                          for logic_type in LogicValueType
                      ]
                      )

TYPE_CATEGORY_NAME = {
    TypeCategory.DATA: DATA_TYPE_CATEGORY,
    TypeCategory.LOGIC: LOGIC_TYPE_CATEGORY,
}


def syntax_of_type_name_in_text(type_name: str) -> str:
    return '"' + type_name + '"'
