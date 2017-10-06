from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_names import SYNTAX_ELEMENT_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId


def syntax_element_cross_ref(syntax_element_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SYNTAX_ELEMENT_ENTITY_TYPE_NAME, syntax_element_name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name,
                                           single_line_description_str,
                                           syntax_element_cross_ref(name))


HERE_DOCUMENT_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.HERE_DOCUMENT.name,
    'A sequence of lines, given using the shell "here document" syntax'
)

REGEX_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.REG_EX.name,
    'A regular expression, using Python syntax'
)

ALL_SYNTAX_ELEMENTS = [
    HERE_DOCUMENT_SYNTAX_ELEMENT,
    REGEX_SYNTAX_ELEMENT,
]


def all_syntax_element_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_SYNTAX_ELEMENTS]
