from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_names import TYPE_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, Name


def type_cross_ref(type_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(TYPE_ENTITY_TYPE_NAME, type_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return SingularAndPluralNameAndCrossReferenceId(name,
                                                    single_line_description_str,
                                                    type_cross_ref(name.singular))


LINES_TRANSFORMER_CONCEPT_INFO = name_and_ref_target(
    Name('file transformer', 'file transformers'),
    'Transforms the lines of a text file.',
)

FILE_SELECTOR_CONCEPT_INFO = name_and_ref_target(
    Name('file selector', 'file selectors'),
    'Selects files in a directory.'
)
