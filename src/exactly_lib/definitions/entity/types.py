from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.str_.name import NameWithGender, NameWithGenderWithFormatting, \
    a_name_with_plural_s


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
        self._single_string_type_name = self._name.singular.replace(' ', '-')

    @property
    def value_type(self) -> ValueType:
        return self._value_type

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
    'A sequence of characters.',
)

LIST_TYPE_INFO = name_and_ref_target(
    ValueType.LIST,
    a_name_with_plural_s('list'),
    'A sequence of zero or more strings.',
)

PATH_TYPE_INFO = name_and_ref_target(
    ValueType.PATH,
    a_name_with_plural_s('path'),
    'A file path, with special support for directories in the ' + formatting.concept_(
        concepts.TCDS_CONCEPT_INFO),
)

LINE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.LINE_MATCHER,
    a_name_with_plural_s('line matcher'),
    'Matches individual text lines.'
)

FILE_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILE_MATCHER,
    a_name_with_plural_s('file matcher'),
    'Matches properties of an existing file - type, name and contents.'
)

FILES_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_MATCHER,
    a_name_with_plural_s('files matcher'),
    'Matches a set of files (e.g. the contents of a directory).'
)

STRING_MATCHER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_MATCHER,
    a_name_with_plural_s('string matcher'),
    'Matches a string (a sequence of new-line separated text lines).',
)

STRING_TRANSFORMER_TYPE_INFO = name_and_ref_target(
    ValueType.STRING_TRANSFORMER,
    a_name_with_plural_s('string transformer'),
    'Transforms a string (a sequence of new-line separated text lines).',
)

PROGRAM_TYPE_INFO = name_and_ref_target(
    ValueType.PROGRAM,
    a_name_with_plural_s('program'),
    'An external program, with optional arguments, and optional transformation of the output.',
)

FILES_CONDITION_TYPE_INFO = name_and_ref_target(
    ValueType.FILES_CONDITION,
    a_name_with_plural_s('files condition'),
    'A condition of existence of a set of named files',
)

ALL_TYPES_INFO_TUPLE = (
    STRING_TYPE_INFO,
    LIST_TYPE_INFO,
    PATH_TYPE_INFO,
    LINE_MATCHER_TYPE_INFO,
    FILE_MATCHER_TYPE_INFO,
    FILES_MATCHER_TYPE_INFO,
    STRING_MATCHER_TYPE_INFO,
    STRING_TRANSFORMER_TYPE_INFO,
    PROGRAM_TYPE_INFO,
    FILES_CONDITION_TYPE_INFO,
)
