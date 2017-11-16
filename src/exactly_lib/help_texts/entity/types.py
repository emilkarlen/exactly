from exactly_lib.help.utils.entity_documentation import command_line_names_as_singular_name
from exactly_lib.help_texts import entity_identifiers
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.concepts import TYPE_CONCEPT_INFO
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, CrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.name import Name, name_with_plural_s

TYPE_ENTITY_TYPE_NAMES = command_line_names_as_singular_name(entity_identifiers.TYPE_ENTITY_TYPE_IDENTIFIER,
                                                             TYPE_CONCEPT_INFO.name)


def type_cross_ref(type_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(TYPE_ENTITY_TYPE_NAMES.identifier,
                                  TYPE_ENTITY_TYPE_NAMES.name.singular,
                                  type_name)


class TypeNameAndCrossReferenceId(SingularAndPluralNameAndCrossReferenceId):
    def __init__(self,
                 name: Name,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(name,
                         single_line_description_str,
                         cross_reference_target)
        self._name = name
        self._single_string_type_name = self._name.singular.replace(' ', '-')

    @property
    def name(self) -> Name:
        return self._name

    @property
    def plural_name(self) -> str:
        return self.name.plural

    @property
    def identifier(self) -> str:
        """Single string variant of singular name, useful for parsing."""
        return self._single_string_type_name

    @property
    def syntax_element_name(self) -> str:
        return formatting.syntax_element(self.singular_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> TypeNameAndCrossReferenceId:
    return TypeNameAndCrossReferenceId(name,
                                       single_line_description_str,
                                       type_cross_ref(name.singular))


STRING_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('string'),
    'A sequence of characters.',
)

LIST_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('list'),
    'A sequence of zero or more strings.',
)

PATH_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('path'),
    'A file path, with special support for directories in the ' + formatting.concept_(
        concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO),
)

LINE_MATCHER_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('line matcher'),
    'Matches individual text lines.'
)

FILE_MATCHER_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('file matcher'),
    'Matches properties of a file, like name and type.'
)

LINES_TRANSFORMER_TYPE_INFO = name_and_ref_target(
    name_with_plural_s('file transformer'),
    'Transforms the lines of a text file.',
)

ALL_TYPES_INFO_TUPLE = (
    STRING_TYPE_INFO,
    LIST_TYPE_INFO,
    PATH_TYPE_INFO,
    LINE_MATCHER_TYPE_INFO,
    FILE_MATCHER_TYPE_INFO,
    LINES_TRANSFORMER_TYPE_INFO,
)
