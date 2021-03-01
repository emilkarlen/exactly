from types import MappingProxyType
from typing import Mapping, Tuple, Sequence

from exactly_lib.definitions import formatting, misc_texts, matcher_model
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.definitions.type_system import TypeNameAndCrossReferenceId, TypeCategory
from exactly_lib.symbol import value_type
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.str_ import english_text
from exactly_lib.util.str_.name import NameWithGender, a_name_with_plural_s, an_name_with_plural_s


def _type_cross_ref(type_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(TYPE_ENTITY_TYPE_NAMES,
                                  type_name)


def name_and_ref_target(value_type: ValueType,
                        type_category: TypeCategory,
                        name: NameWithGender,
                        single_line_description_str: str) -> TypeNameAndCrossReferenceId:
    return TypeNameAndCrossReferenceId(value_type,
                                       type_category,
                                       name,
                                       single_line_description_str,
                                       _type_cross_ref(name.singular))


STRING_TYPE_INFO = name_and_ref_target(
    ValueType.STRING,
    TypeCategory.DATA,
    a_name_with_plural_s('string'),
    'A sequence of characters',
)

LIST_TYPE_INFO = name_and_ref_target(
    ValueType.LIST,
    TypeCategory.DATA,
    a_name_with_plural_s('list'),
    'A sequence of zero or more {} elements'.format(STRING_TYPE_INFO.singular_name),
)

PATH_TYPE_INFO = name_and_ref_target(
    ValueType.PATH,
    TypeCategory.DATA,
    a_name_with_plural_s('path'),
    'A file path, with special support for directories in the ' + formatting.concept_(
        concepts.TCDS_CONCEPT_INFO),
)

INTEGER_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.INTEGER_MATCHER,
    TypeCategory.LOGIC,
    an_name_with_plural_s('integer-matcher'),
    'Matches {model:a}'.format(
        model=matcher_model.INTEGER_MATCHER_MODEL
    )
)

LINE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.LINE_MATCHER,
    TypeCategory.LOGIC,
    a_name_with_plural_s('line-matcher'),
    'Matches individual {model:s} of {text_model:a}'.format(
        model=matcher_model.LINE_MATCHER_MODEL,
        text_model=matcher_model.TEXT_MODEL,
    )
)

FILE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILE_MATCHER,
    TypeCategory.LOGIC,
    a_name_with_plural_s('file-matcher'),
    'Matches properties of an existing {model} - type, name and contents'.format(
        model=matcher_model.FILE_MATCHER_MODEL,
    ),
)

FILES_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_MATCHER,
    TypeCategory.LOGIC,
    a_name_with_plural_s('files-matcher'),
    'Matches {model:a} (e.g. the contents of a directory)'.format(
        model=matcher_model.FILES_MATCHER_MODEL,
    ),
)

STRING_SOURCE_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_SOURCE,
    TypeCategory.LOGIC,
    a_name_with_plural_s('text-source'),
    'Produces {:a}, from various sources'.format(
        matcher_model.TEXT_MODEL
    ),
)

STRING_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_MATCHER,
    TypeCategory.LOGIC,
    a_name_with_plural_s('text-matcher'),
    'Matches {model:a}'.format(
        model=matcher_model.TEXT_MODEL,
    ),
)

STRING_TRANSFORMER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_TRANSFORMER,
    TypeCategory.LOGIC,
    a_name_with_plural_s('text-transformer'),
    'Transforms {model:a}'.format(
        model=matcher_model.TEXT_MODEL,
    ),
)

PROGRAM_TYPE_INFO = name_and_ref_target(
    ValueType.PROGRAM,
    TypeCategory.LOGIC,
    a_name_with_plural_s('program'),
    '{:a/u}, with optional arguments, and optional transformation of the output'.format(
        misc_texts.EXTERNAL_PROGRAM
    ),
)

FILES_CONDITION_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_CONDITION,
    TypeCategory.LOGIC,
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
    FILES_CONDITION_TYPE_INFO,
    STRING_SOURCE_TYPE_INFO,
    STRING_MATCHER_TYPE_INFO,
    STRING_TRANSFORMER_TYPE_INFO,
    PROGRAM_TYPE_INFO,
)

VALUE_TYPE_2_TYPES_INFO_DICT: Mapping[ValueType, TypeNameAndCrossReferenceId] = MappingProxyType({
    ti.value_type: ti
    for ti in ALL_TYPES_INFO_TUPLE
})

TYPES_WITH_W_STR_RENDERING: Tuple[TypeNameAndCrossReferenceId, ...] = tuple([
    VALUE_TYPE_2_TYPES_INFO_DICT[vt]
    for vt in value_type.VALUE_TYPES_W_STR_RENDERING
])


def types__or_list(types: Sequence[ValueType]) -> str:
    return english_text.or_sequence([
        formatting.keyword(VALUE_TYPE_2_TYPES_INFO_DICT[t].singular_name) for
        t in types
    ])


def types__and_list(types: Sequence[ValueType]) -> str:
    return english_text.and_sequence([
        formatting.keyword(VALUE_TYPE_2_TYPES_INFO_DICT[t].singular_name) for
        t in types
    ])


def a_ref_to_a_symbol_w_string_conversion__sentence() -> str:
    return a_ref_to_a_symbol__of_either_types(value_type.VALUE_TYPES_W_STR_RENDERING)


def a_ref_to_a_symbol__of_either_types(types: Sequence[ValueType]) -> str:
    return _A_REF_TO_A_SYMBOL_OF_EITHER_TYPES__SENTENCE.format(
        formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
        types__or_list(types)
    )


_A_REF_TO_A_SYMBOL_OF_EITHER_TYPES__SENTENCE = """\
A reference to a {} defined as either {}."""
