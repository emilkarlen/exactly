import enum
from enum import Enum
from types import MappingProxyType

from exactly_lib.definitions.entity import types
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.str_.name import NumberOfItemsString, Name

DATA_TYPE_CATEGORY_NAME = 'data'
LOGIC_TYPE_CATEGORY_NAME = 'logic'

LIST_ELEMENT = 'ELEMENT'
NUMBER_OF_LIST_ELEMENTS = NumberOfItemsString(Name.new_with_plural_s('element'))

NUMBER_OF_STRING_CHARACTERS = NumberOfItemsString(Name.new_with_plural_s('character'))

TYPE_INFO_DICT = MappingProxyType({
    ValueType.STRING: types.STRING_TYPE_INFO,
    ValueType.PATH: types.PATH_TYPE_INFO,
    ValueType.LIST: types.LIST_TYPE_INFO,
    ValueType.INTEGER_MATCHER: types.INTEGER_MATCHER_TYPE_INFO,
    ValueType.LINE_MATCHER: types.LINE_MATCHER_TYPE_INFO,
    ValueType.FILE_MATCHER: types.FILE_MATCHER_TYPE_INFO,
    ValueType.FILES_MATCHER: types.FILES_MATCHER_TYPE_INFO,
    ValueType.STRING_MATCHER: types.STRING_MATCHER_TYPE_INFO,
    ValueType.STRING_TRANSFORMER: types.STRING_TRANSFORMER_TYPE_INFO,
    ValueType.PROGRAM: types.PROGRAM_TYPE_INFO,
    ValueType.FILES_CONDITION: types.FILES_CONDITION_TYPE_INFO,
})


@enum.unique
class TypeCategory(Enum):
    DATA = 1
    LOGIC = 2


TYPE_CATEGORY_NAME = MappingProxyType({
    TypeCategory.DATA: DATA_TYPE_CATEGORY_NAME,
    TypeCategory.LOGIC: LOGIC_TYPE_CATEGORY_NAME,
})
VALUE_TYPE_2_TYPE_CATEGORY = MappingProxyType({
    ValueType.STRING: TypeCategory.DATA,
    ValueType.PATH: TypeCategory.DATA,
    ValueType.LIST: TypeCategory.DATA,
    ValueType.FILES_CONDITION: TypeCategory.DATA,

    ValueType.INTEGER_MATCHER: TypeCategory.LOGIC,
    ValueType.FILE_MATCHER: TypeCategory.LOGIC,
    ValueType.FILES_MATCHER: TypeCategory.LOGIC,
    ValueType.LINE_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_TRANSFORMER: TypeCategory.LOGIC,
    ValueType.PROGRAM: TypeCategory.LOGIC,
})
