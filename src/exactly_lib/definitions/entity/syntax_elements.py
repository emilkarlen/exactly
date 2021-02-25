from typing import Optional

from exactly_lib.definitions import type_system
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.entity.all_entity_types import SYNTAX_ELEMENT_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import StringText


class SyntaxElementInfo(SingularNameAndCrossReferenceId):
    def __init__(self,
                 singular_name: str,
                 type_category: Optional[TypeCategory],
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(singular_name, single_line_description_str, cross_reference_target)
        self._type_category = type_category

    @property
    def type_category(self) -> Optional[TypeCategory]:
        return self._type_category

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

    @property
    def zero_or_more(self) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.ZERO_OR_MORE,
                        self.argument)


def syntax_element_cross_ref(syntax_element_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
                                  syntax_element_name)


def name_and_ref_target(name: str,
                        type_category: Optional[TypeCategory],
                        single_line_description_str: str) -> SyntaxElementInfo:
    return SyntaxElementInfo(name,
                             type_category,
                             single_line_description_str,
                             syntax_element_cross_ref(name))


def _name_and_ref_target__non_type(name: str,
                                   single_line_description_str: str,
                                   ) -> SyntaxElementInfo:
    return SyntaxElementInfo(name,
                             None,
                             single_line_description_str,
                             syntax_element_cross_ref(name))


def _name_and_ref_target_of_type(type_info: type_system.TypeNameAndCrossReferenceId) -> SyntaxElementInfo:
    return name_and_ref_target(type_info.syntax_element_identifier,
                               type_info.type_category,
                               type_info.single_line_description_str)


STRING_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_TYPE_INFO)

LIST_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LIST_TYPE_INFO)

PATH_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.PATH_TYPE_INFO)

INTEGER_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.INTEGER_MATCHER_TYPE_INFO)

FILE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.FILE_MATCHER_TYPE_INFO)

LINE_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.LINE_MATCHER_TYPE_INFO)

STRING_SOURCE_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_SOURCE_TYPE_INFO)

STRING_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_MATCHER_TYPE_INFO)

STRING_TRANSFORMER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.STRING_TRANSFORMER_TYPE_INFO)

PROGRAM_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.PROGRAM_TYPE_INFO)

FILES_MATCHER_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.FILES_MATCHER_TYPE_INFO)

FILES_CONDITION_SYNTAX_ELEMENT = _name_and_ref_target_of_type(types.FILES_CONDITION_TYPE_INFO)

SHELL_COMMAND_LINE_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'SHELL-COMMAND-LINE',
    'A shell command line, as the remaining part of the current line'
)

SYMBOL_NAME_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'SYMBOL-NAME',
    'The name of a symbol'
)

SYMBOL_REFERENCE_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'SYMBOL-REFERENCE',
    'A reference to a symbol using special reference syntax'
)

HERE_DOCUMENT_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'HERE-DOCUMENT',
    'A {string} value, given as a sequence of lines, resembling shell "here document" syntax'.format(
        string=types.STRING_TYPE_INFO.singular_name)
)

REGEX_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'REGEX',
    'A regular expression, using Python syntax'
)

GLOB_PATTERN_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'GLOB-PATTERN',
    'A file name glob pattern'
)

INTEGER_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'INTEGER',
    'An integer expression'
)

PROGRAM_ARGUMENT_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'PROGRAM-ARGUMENT',
    ('An individual {string_type}, or a list of {string_type:s}, '
     'with additional features for text-until-end-of-line and references to existing files'
     ).format(string_type=types.STRING_TYPE_INFO.name),
)

ACT_INTERPRETER_SYNTAX_ELEMENT = _name_and_ref_target__non_type(
    'ACT-INTERPRETER',
    'An interpreter program that executes source code of the {:emphasis} phase'.format(
        phase_names.ACT
    )
)

ALL_ELEMENTS_CORRESPONDING_TO_TYPES = (
    STRING_SYNTAX_ELEMENT,
    LIST_SYNTAX_ELEMENT,
    PATH_SYNTAX_ELEMENT,
    INTEGER_MATCHER_SYNTAX_ELEMENT,
    LINE_MATCHER_SYNTAX_ELEMENT,
    FILE_MATCHER_SYNTAX_ELEMENT,
    FILES_MATCHER_SYNTAX_ELEMENT,
    FILES_CONDITION_SYNTAX_ELEMENT,
    STRING_SOURCE_SYNTAX_ELEMENT,
    STRING_MATCHER_SYNTAX_ELEMENT,
    STRING_TRANSFORMER_SYNTAX_ELEMENT,
    PROGRAM_SYNTAX_ELEMENT,
)
