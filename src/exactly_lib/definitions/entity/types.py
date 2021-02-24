from types import MappingProxyType
from typing import Mapping, Tuple

from exactly_lib.definitions import formatting, misc_texts, doc_format, matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.symbol import value_type
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.str_ import english_text
from exactly_lib.util.str_.name import NameWithGender, NameWithGenderWithFormatting, \
    a_name_with_plural_s, an_name_with_plural_s
from exactly_lib.util.textformat.structure.core import StringText


def type_cross_ref(type_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(TYPE_ENTITY_TYPE_NAMES,
                                  type_name)


class TypeNameAndCrossReferenceId(SingularAndPluralNameAndCrossReferenceId):
    def __init__(self,
                 value_type: ValueType,
                 name: NameWithGender,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(name,
                         single_line_description_str,
                         cross_reference_target)
        self._value_type = value_type
        self._name = formatting.type_name_with_formatting(name)
        self._single_string_type_name = self._name.singular

    @property
    def value_type(self) -> ValueType:
        return self._value_type

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


def name_and_ref_target(value_type: ValueType,
                        name: NameWithGender,
                        single_line_description_str: str) -> TypeNameAndCrossReferenceId:
    return TypeNameAndCrossReferenceId(value_type,
                                       name,
                                       single_line_description_str,
                                       type_cross_ref(name.singular))


STRING_TYPE_INFO = name_and_ref_target(
    ValueType.STRING,
    a_name_with_plural_s('string'),
    'A sequence of characters',
)

LIST_TYPE_INFO = name_and_ref_target(
    ValueType.LIST,
    a_name_with_plural_s('list'),
    'A sequence of zero or more {} elements'.format(STRING_TYPE_INFO.singular_name),
)

PATH_TYPE_INFO = name_and_ref_target(
    ValueType.PATH,
    a_name_with_plural_s('path'),
    'A file path, with special support for directories in the ' + formatting.concept_(
        concepts.TCDS_CONCEPT_INFO),
)

INTEGER_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.INTEGER_MATCHER,
    an_name_with_plural_s('integer-matcher'),
    'Matches {model:a}'.format(
        model=matcher_model.INTEGER_MATCHER_MODEL
    )
)

LINE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.LINE_MATCHER,
    a_name_with_plural_s('line-matcher'),
    'Matches individual {model:s} of {text_model:a}'.format(
        model=matcher_model.LINE_MATCHER_MODEL,
        text_model=matcher_model.TEXT_MODEL,
    )
)

FILE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILE_MATCHER,
    a_name_with_plural_s('file-matcher'),
    'Matches properties of an existing {model} - type, name and contents'.format(
        model=matcher_model.FILE_MATCHER_MODEL,
    ),
)

FILES_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_MATCHER,
    a_name_with_plural_s('files-matcher'),
    'Matches {model:a} (e.g. the contents of a directory)'.format(
        model=matcher_model.FILES_MATCHER_MODEL,
    ),
)

STRING_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_MATCHER,
    a_name_with_plural_s('string-matcher'),
    'Matches {model:a} (a sequence of characters)'.format(
        model=matcher_model.TEXT_MODEL,
    ),
)

STRING_TRANSFORMER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_TRANSFORMER,
    a_name_with_plural_s('string-transformer'),
    'Transforms {model:a} (a sequence of characters)'.format(
        model=matcher_model.TEXT_MODEL,
    ),
)

PROGRAM_TYPE_INFO = name_and_ref_target(
    ValueType.PROGRAM,
    a_name_with_plural_s('program'),
    '{:a/u}, with optional arguments, and optional transformation of the output'.format(
        misc_texts.EXTERNAL_PROGRAM
    ),
)

FILES_CONDITION_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_CONDITION,
    a_name_with_plural_s('files-condition'),
    'A condition of existence of a set of named files',
)

ALL_TYPES_INFO_TUPLE = (
    STRING_TYPE_INFO,
    LIST_TYPE_INFO,
    PATH_TYPE_INFO,
    INTEGER_MATCHER_TYPE_INFO,
    LINE_MATCHER_TYPE_INFO,
    FILE_MATCHER_TYPE_INFO,
    FILES_MATCHER_TYPE_INFO,
    STRING_MATCHER_TYPE_INFO,
    STRING_TRANSFORMER_TYPE_INFO,
    PROGRAM_TYPE_INFO,
    FILES_CONDITION_TYPE_INFO,
)

VALUE_TYPE_2_TYPES_INFO_DICT: Mapping[ValueType, TypeNameAndCrossReferenceId] = MappingProxyType({
    ti.value_type: ti
    for ti in ALL_TYPES_INFO_TUPLE
})

TYPES_WITH_STRING_CONVERSION: Tuple[TypeNameAndCrossReferenceId, ...] = tuple([
    VALUE_TYPE_2_TYPES_INFO_DICT[vt]
    for vt in value_type.VALUE_TYPES_CONVERTIBLE_TO_STRING
])


def types_w_string_conversion__or_list() -> str:
    return english_text.or_sequence([
        formatting.keyword(dt.singular_name) for
        dt in TYPES_WITH_STRING_CONVERSION
    ])


def a_ref_to_a_symbol_w_string_conversion__sentence() -> str:
    return _A_REF_TO_A_SYMBOL_W_STRING_CONVERSION__SENTENCE.format(
        formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
        types_w_string_conversion__or_list()
    )


_A_REF_TO_A_SYMBOL_W_STRING_CONVERSION__SENTENCE = """\
A reference to a {} defined as either {}."""
