from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ActComparisonActualFileForFileRef, \
    ComparisonActualFileConstructor
from exactly_lib.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_checker import \
    FileContentsCheckerHelp
from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import path_element
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration, parse_file_ref
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem

ACTUAL_PATH_ARGUMENT = a.Named('ACTUAL-PATH')


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(parser(instruction_name),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        self.actual_file_arg = ACTUAL_PATH_ARGUMENT
        super().__init__(name, {
            'checked_file': self.actual_file_arg.name,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    self.actual_file_arg)
        self._help_parts = FileContentsCheckerHelp(name,
                                                   self.actual_file_arg.name,
                                                   [self.actual_file])

    def single_line_description(self) -> str:
        return 'Tests the contents of a file'

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants__file(self.actual_file_arg)

    def _cls(self, additional_argument_usages: list) -> str:
        return self._cl_syntax_for_args([self.actual_file] + additional_argument_usages)

    def syntax_element_descriptions(self) -> list:
        actual_file_arg_sed = path_element(
            self.actual_file_arg.name,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            self._paragraphs(the_path_of("the file who's contents is checked."))
        )

        return (self._help_parts.syntax_element_descriptions_at_top() +
                [actual_file_arg_sed] +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_targets(self) -> list:
        return self._help_parts.see_also_targets__file()


def parser(instruction_name: str) -> AssertPhaseInstructionParser:
    return parse_instruction.Parser(instruction_name, _ActualFileParser())


class _ActualFileParser(ComparisonActualFileParser):
    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        parser.require_is_not_at_eol(
            'Missing {actual_file} argument'.format(actual_file=ACTUAL_PATH_ARGUMENT.name))
        file_ref = parse_file_ref.parse_file_ref_from_token_parser(ACTUAL_RELATIVITY_CONFIGURATION,
                                                                   parser)
        return actual_files.ComparisonActualFileConstructorForConstant(ActComparisonActualFileForFileRef(file_ref))


ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        parse_file_ref.ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX_OR_ABSOLUTE,
        RelOptionType.REL_CWD),
    'PATH',
    True)

_MAIN_DESCRIPTION_REST = """\
FAILs if {checked_file} is not an existing regular file.
"""
