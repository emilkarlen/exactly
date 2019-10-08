from exactly_lib.definitions.entity import types
from exactly_lib.type_system.value_type import ValueType, DataValueType, TypeCategory, LogicValueType
from exactly_lib.util.name import NumberOfItemsString, Name

DATA_TYPE_CATEGORY_NAME = 'data'
LOGIC_TYPE_CATEGORY_NAME = 'logic'


def _type_identifier(type_name: str) -> str:
    return type_name.replace(' ', '-')


LIST_ELEMENT = 'ELEMENT'
NUMBER_OF_LIST_ELEMENTS = NumberOfItemsString(Name.new_with_plural_s('element'))

NUMBER_OF_STRING_CHARACTERS = NumberOfItemsString(Name.new_with_plural_s('character'))

DATA_TYPE_INFO_DICT = {
    DataValueType.STRING: types.STRING_TYPE_INFO,
    DataValueType.PATH: types.PATH_TYPE_INFO,
    DataValueType.LIST: types.LIST_TYPE_INFO,
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
    LogicValueType.LINE_MATCHER: types.LINE_MATCHER_TYPE_INFO,
    LogicValueType.FILE_MATCHER: types.FILE_MATCHER_TYPE_INFO,
    LogicValueType.FILES_MATCHER: types.FILES_MATCHER_TYPE_INFO,
    LogicValueType.STRING_MATCHER: types.STRING_MATCHER_TYPE_INFO,
    LogicValueType.STRING_TRANSFORMER: types.STRING_TRANSFORMER_TYPE_INFO,
    LogicValueType.PROGRAM: types.PROGRAM_TYPE_INFO,
}

LOGIC_TYPE_2_VALUE_TYPE = {
    LogicValueType.LINE_MATCHER: ValueType.LINE_MATCHER,
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.FILES_MATCHER: ValueType.FILES_MATCHER,
    LogicValueType.STRING_MATCHER: ValueType.STRING_MATCHER,
    LogicValueType.STRING_TRANSFORMER: ValueType.STRING_TRANSFORMER,
    LogicValueType.PROGRAM: ValueType.PROGRAM,
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
    TypeCategory.DATA: DATA_TYPE_CATEGORY_NAME,
    TypeCategory.LOGIC: LOGIC_TYPE_CATEGORY_NAME,
}
