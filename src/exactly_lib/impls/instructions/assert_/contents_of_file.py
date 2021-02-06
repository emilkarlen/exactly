from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import actual_file_attributes, file_types, formatting
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls import common_arguments
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.impls.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.impls.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor
from exactly_lib.impls.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.impls.types.file_matcher import file_or_dir_contents_doc
from exactly_lib.impls.types.path import parse_path, path_relativities, rel_opts_configuration
from exactly_lib.impls.types.path.relative_path_options_documentation import path_element
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case import reserved_words
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents

ACTUAL_PATH_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(parser(instruction_name),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        self.actual_file_arg = ACTUAL_PATH_ARGUMENT
        super().__init__(name, {
            'checked_file': self.actual_file_arg.name,
            'contents_matcher': formatting.syntax_element_(syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT),
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'file': file_types.REGULAR,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    self.actual_file_arg)

    def single_line_description(self) -> str:
        return self._tp.format('Tests the contents of {file:a}')

    def main_description_rest(self) -> List[ParagraphItem]:
        return []

    def outcome(self) -> SectionContents:
        return file_or_dir_contents_doc.outcome(ACTUAL_PATH_ARGUMENT.name,
                                                FileType.REGULAR)

    def notes(self) -> SectionContents:
        return SectionContents(file_or_dir_contents_doc.notes())

    def invokation_variants(self) -> List[InvokationVariant]:
        actual_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                   self.actual_file_arg)
        return [
            invokation_variant_from_args([
                actual_file_arg,
                common_arguments.RESERVED_WORD__COLON,
                syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            ],
                self._tp.fnap(_MAIN_INVOKATION__FILE__SYNTAX_DESCRIPTION)),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        actual_file_arg_sed = path_element(
            self.actual_file_arg.name,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            self._tp.fnap(the_path_of("the file who's contents is checked."))
        )

        return [actual_file_arg_sed]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
        ])


def parser(instruction_name: str) -> AssertPhaseInstructionParser:
    return parse_instruction.Parser(instruction_name, _ActualFileParser())


class _ActualFileParser(ComparisonActualFileParser):
    def __init__(self):
        super().__init__()
        self._path_parser = parse_path.PathParser(ACTUAL_RELATIVITY_CONFIGURATION)

    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        parser.require_is_not_at_eol(
            'Missing {actual_file} argument'.format(actual_file=ACTUAL_PATH_ARGUMENT.name))
        path = self._path_parser.parse_from_token_parser(parser)
        parser.consume_mandatory_constant_unquoted_string(reserved_words.COLON,
                                                          must_be_on_current_line=False)
        return actual_files.ConstructorForPath(path,
                                               actual_file_attributes.PLAIN_FILE_OBJECT_NAME,
                                               True)


ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    path_relativities.PATH_ASSERTION_REL_OPTS_CONF,
    ACTUAL_PATH_ARGUMENT.name,
    True)

_MAIN_INVOKATION__FILE__SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {contents_matcher}.
"""
