from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.entity.all_entity_types import SYNTAX_ELEMENT_ENTITY_TYPE_NAMES
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import StringText


class SyntaxElementInfo(SingularNameAndCrossReferenceId):
    @property
    def singular_name_text(self) -> StringText:
        return syntax_text(self._singular_name)

    @property
    def argument(self) -> a.Named:
        return a.Named(self.singular_name)

    @property
    def single_mandatory(self) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        self.argument)

    @property
    def single_optional(self) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.OPTIONAL,
                        self.argument)


def syntax_element_cross_ref(syntax_element_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
                                  syntax_element_name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SyntaxElementInfo:
    return SyntaxElementInfo(name,
                             single_line_description_str,
                             syntax_element_cross_ref(name))


def _name_and_ref_target_of_type(type_info: types.TypeNameAndCrossReferenceId) -> SyntaxElementInfo:
    return name_and_ref_target(type_info.syntax_element_name,
                               type_info.single_line_description_str)


STRING_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_TYPE_INFO)

LIST_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LIST_TYPE_INFO)

PATH_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.PATH_TYPE_INFO)

FILE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.FILE_MATCHER_TYPE_INFO)

LINE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LINE_MATCHER_TYPE_INFO)

LINES_TRANSFORMER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LINES_TRANSFORMER_TYPE_INFO)

SYMBOL_NAME_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.SYMBOL_NAME_ARGUMENT.name,
    'The name of a symbol'
)

SYMBOL_REFERENCE_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.SYMBOL_REFERENCE.name,
    'A reference to a symbol using special reference syntax'
)

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

INTEGER_SYNTAX_ELEMENT = name_and_ref_target(
    instruction_arguments.INTEGER_ARGUMENT.name,
    'An integer expression'
)

INTEGER_COMPARISON_SYNTAX_ELEMENT = name_and_ref_target(
    'INTEGER-COMPARISON',
    'Matches an integer value using relational comparison with a given ' + INTEGER_SYNTAX_ELEMENT.argument.name
)

FILE_CONTENTS_MATCHER = name_and_ref_target(
    'FILE-CONTENTS-MATCHER',
    'Matches the contents of a regular file'
)

ALL_SYNTAX_ELEMENTS = (

    SYMBOL_NAME_SYNTAX_ELEMENT,
    SYMBOL_REFERENCE_SYNTAX_ELEMENT,

    HERE_DOCUMENT_SYNTAX_ELEMENT,

    REGEX_SYNTAX_ELEMENT,
    GLOB_PATTERN_SYNTAX_ELEMENT,

    INTEGER_SYNTAX_ELEMENT,
    INTEGER_COMPARISON_SYNTAX_ELEMENT,

    FILE_CONTENTS_MATCHER,

    STRING_SYNTAX_ELEMENT,
    LIST_SYNTAX_ELEMENT,
    PATH_SYNTAX_ELEMENT,

    FILE_MATCHER_SYNTAX_ELEMENT,
    LINE_MATCHER_SYNTAX_ELEMENT,
    LINES_TRANSFORMER_SYNTAX_ELEMENT,
)


def all_syntax_element_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_SYNTAX_ELEMENTS]
