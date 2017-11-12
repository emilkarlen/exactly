from exactly_lib.help_texts.entity import types
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType

DATA_TYPE_CATEGORY = 'data'
LOGIC_TYPE_CATEGORY = 'logic'


def _type_identifier(type_name: str) -> str:
    return type_name.replace(' ', '-')


LIST_ELEMENT = 'ELEMENT'


class TypeInfo:
    def __init__(self,
                 info: types.TypeNameAndCrossReferenceId):
        self.type_name = info.identifier
        self.value_name = info.syntax_element_name
        self.concept_info = info


DATA_TYPE_INFO_DICT = {
    DataValueType.STRING: TypeInfo(types.STRING_TYPE_INFO),
    DataValueType.PATH: TypeInfo(types.PATH_TYPE_INFO),
    DataValueType.LIST: TypeInfo(types.LIST_TYPE_INFO),
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
    LogicValueType.LINE_MATCHER: TypeInfo(types.LINE_MATCHER_TYPE_INFO),
    LogicValueType.FILE_MATCHER: TypeInfo(types.FILE_MATCHER_TYPE_INFO),
    LogicValueType.LINES_TRANSFORMER: TypeInfo(types.LINES_TRANSFORMER_TYPE_INFO),
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
