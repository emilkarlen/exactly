from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.names.formatting import syntax_element
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType

DATA_TYPE_CATEGORY = 'data'
LOGIC_TYPE_CATEGORY = 'logic'


def _type_name(type_name: str) -> str:
    return type_name.replace(' ', '-')


PATH_TYPE = _type_name(types.PATH_CONCEPT_INFO.singular_name)
PATH_SYNTAX_ELEMENT = syntax_element(types.PATH_CONCEPT_INFO.singular_name)

STRING_TYPE = _type_name(types.STRING_CONCEPT_INFO.singular_name)
STRING_SYNTAX_ELEMENT = syntax_element(types.STRING_CONCEPT_INFO.singular_name)

LIST_TYPE = _type_name(types.LIST_CONCEPT_INFO.singular_name)
LIST_SYNTAX_ELEMENT = syntax_element(types.LIST_CONCEPT_INFO.singular_name)
LIST_ELEMENT = 'ELEMENT'

LINE_MATCHER_TYPE = _type_name(types.LINE_MATCHER_CONCEPT_INFO.singular_name)
LINE_MATCHER_SYNTAX_ELEMENT = syntax_element(types.LINE_MATCHER_CONCEPT_INFO.singular_name)

FILE_MATCHER_TYPE = _type_name(types.FILE_MATCHER_CONCEPT_INFO.singular_name)
FILE_MATCHER_SYNTAX_ELEMENT = syntax_element(types.FILE_MATCHER_CONCEPT_INFO.singular_name)

LINES_TRANSFORMER_TYPE = _type_name(types.LINES_TRANSFORMER_CONCEPT_INFO.singular_name)
LINES_TRANSFORMER_SYNTAX_ELEMENT = syntax_element(types.LINES_TRANSFORMER_CONCEPT_INFO.singular_name)


class TypeInfo:
    def __init__(self,
                 info: types.TypeNameAndCrossReferenceId):
        self.type_name = info.single_string_name
        self.value_name = info.syntax_element_name
        self.concept_info = info


DATA_TYPE_INFO_DICT = {
    DataValueType.STRING: TypeInfo(types.STRING_CONCEPT_INFO),
    DataValueType.PATH: TypeInfo(types.PATH_CONCEPT_INFO),
    DataValueType.LIST: TypeInfo(types.LIST_CONCEPT_INFO),
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
    LogicValueType.LINE_MATCHER: TypeInfo(types.LINE_MATCHER_CONCEPT_INFO),
    LogicValueType.FILE_MATCHER: TypeInfo(types.FILE_MATCHER_CONCEPT_INFO),
    LogicValueType.LINES_TRANSFORMER: TypeInfo(types.LINES_TRANSFORMER_CONCEPT_INFO),
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
