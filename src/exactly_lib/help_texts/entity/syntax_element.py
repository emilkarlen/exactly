from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.entity_names import SYNTAX_ELEMENT_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId


def syntax_element_cross_ref(syntax_element_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SYNTAX_ELEMENT_ENTITY_TYPE_NAME, syntax_element_name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name,
                                           single_line_description_str,
                                           syntax_element_cross_ref(name))


def _name_and_ref_target_of_type(type_info: types.TypeNameAndCrossReferenceId) -> SingularNameAndCrossReferenceId:
    return name_and_ref_target(type_info.syntax_element_name,
                               type_info.single_line_description_str)


STRING_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_TYPE_INFO)

LIST_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LIST_TYPE_INFO)

PATH_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.PATH_TYPE_INFO)

FILE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.FILE_MATCHER_TYPE_INFO)

LINE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LINE_MATCHER_TYPE_INFO)

LINES_TRANSFORMER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LINES_TRANSFORMER_TYPE_INFO)

HERE_DOCUMENT_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.HERE_DOCUMENT.name,
    'A {string} value, given as a sequence of lines, resembling shell "here document" syntax'.format(
        string=types.STRING_TYPE_INFO.singular_name)
)

REGEX_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.REG_EX.name,
    'A regular expression, using Python syntax'
)

GLOB_PATTERN_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.GLOB_PATTERN.name,
    'A shell glob pattern'
)

ALL_SYNTAX_ELEMENTS = [

    HERE_DOCUMENT_SYNTAX_ELEMENT,
    REGEX_SYNTAX_ELEMENT,
    GLOB_PATTERN_SYNTAX_ELEMENT,

    STRING_SYNTAX_ELEMENT,
    LIST_SYNTAX_ELEMENT,
    PATH_SYNTAX_ELEMENT,

    FILE_MATCHER_SYNTAX_ELEMENT,
    LINE_MATCHER_SYNTAX_ELEMENT,
    LINES_TRANSFORMER_SYNTAX_ELEMENT,
]


def all_syntax_element_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_SYNTAX_ELEMENTS]
