import enum
from enum import Enum
from types import MappingProxyType

from exactly_lib.definitions import formatting, doc_format
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.str_.name import NumberOfItemsString, Name, NameWithGender, NameWithGenderWithFormatting
from exactly_lib.util.textformat.structure.core import StringText

DATA_TYPE_CATEGORY_NAME = 'Data types'
LOGIC_TYPE_CATEGORY_NAME = 'Types involving logic'

LIST_ELEMENT = 'ELEMENT'
NUMBER_OF_LIST_ELEMENTS = NumberOfItemsString(Name.new_with_plural_s('element'))

NUMBER_OF_STRING_CHARACTERS = NumberOfItemsString(Name.new_with_plural_s('character'))


@enum.unique
class TypeCategory(Enum):
    """Type categories, in display order"""
    DATA = 1
    LOGIC = 2


TYPE_CATEGORY_NAME = MappingProxyType({
    TypeCategory.DATA: DATA_TYPE_CATEGORY_NAME,
    TypeCategory.LOGIC: LOGIC_TYPE_CATEGORY_NAME,
})


class TypeNameAndCrossReferenceId(SingularAndPluralNameAndCrossReferenceId):
    def __init__(self,
                 value_type: ValueType,
                 type_category: TypeCategory,
                 name: NameWithGender,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(name,
                         single_line_description_str,
                         cross_reference_target)
        self._value_type = value_type
        self._type_category = type_category
        self._name = formatting.type_name_with_formatting(name)
        self._single_string_type_name = self._name.singular

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def type_category(self) -> TypeCategory:
        return self._type_category

    @property
    def singular_name_text(self) -> StringText:
        return doc_format.syntax_text(self._single_string_type_name)

    @property
    def name(self) -> NameWithGenderWithFormatting:
        return self._name

    @property
    def plural_name(self) -> str:
        return self.name.plural

    @property
    def identifier(self) -> str:
        """Single string variant of singular name, useful for parsing."""
        return self._single_string_type_name

    @property
    def syntax_element_identifier(self) -> str:
        """The syntax element name"""
        return self._single_string_type_name.upper()

    @property
    def syntax_element_name(self) -> str:
        return formatting.syntax_element(self.singular_name)
