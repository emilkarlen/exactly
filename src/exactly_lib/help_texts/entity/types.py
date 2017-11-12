from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_names import TYPE_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.util.name import Name


def type_cross_ref(type_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(TYPE_ENTITY_TYPE_NAME, type_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return SingularAndPluralNameAndCrossReferenceId(name,
                                                    single_line_description_str,
                                                    type_cross_ref(name.singular))


STRING_CONCEPT_INFO = name_and_ref_target(
    Name('string', 'strings'),
    'A sequence of characters.',
)

LIST_CONCEPT_INFO = name_and_ref_target(
    Name('list', 'lists'),
    'A sequence of zero or more strings.',
)

PATH_CONCEPT_INFO = name_and_ref_target(
    Name('path', 'paths'),
    'A path of a file or directory, with special support for the test case directories.',
)

LINE_MATCHER_CONCEPT_INFO = name_and_ref_target(
    Name('line matcher', 'line matchers'),
    'Matches individual text lines.'
)

FILE_MATCHER_CONCEPT_INFO = name_and_ref_target(
    Name('file matcher', 'file matchers'),
    'Matches properties of a file, like name and type.'
)

LINES_TRANSFORMER_CONCEPT_INFO = name_and_ref_target(
    Name('file transformer', 'file transformers'),
    'Transforms the lines of a text file.',
)

ALL_TYPE_CONCEPT_INFO_TUPLE = (
    STRING_CONCEPT_INFO,
    LIST_CONCEPT_INFO,
    PATH_CONCEPT_INFO,
    LINE_MATCHER_CONCEPT_INFO,
    FILE_MATCHER_CONCEPT_INFO,
    LINES_TRANSFORMER_CONCEPT_INFO,
)
