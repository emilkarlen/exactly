from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ActComparisonActualFileForFileRef
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_checker import \
    FileContentsCheckerHelp
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import path_element
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration, parse_file_ref
from exactly_lib.util.cli_syntax.elements import argument as a

ACTUAL_PATH_ARGUMENT = a.Named('ACTUAL-PATH')


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
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

    def main_description_rest(self) -> list:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

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
        return self._help_parts.see_also_targets()


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parser.TokenParser), 'Must have a TokenParser'  # Type info for IDE
            token_parser.require_is_not_at_eol(
                'Missing {actual_file} argument'.format(actual_file=ACTUAL_PATH_ARGUMENT.name))

            comparison_target = parse_actual_file_argument_from_token_parser(token_parser)
            return parse_instruction.parse_instruction(comparison_target,
                                                       token_parser)


ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        parse_file_ref.ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX_OR_ABSOLUTE,
        RelOptionType.REL_CWD),
    'PATH',
    True)


def parse_actual_file_argument(source: ParseSource) -> ComparisonActualFile:
    file_ref = parse_file_ref.parse_file_ref_from_parse_source(source,
                                                               ACTUAL_RELATIVITY_CONFIGURATION)
    return ActComparisonActualFileForFileRef(file_ref)


def parse_actual_file_argument_from_token_parser(token_parser: token_stream_parser.TokenParser
                                                 ) -> ComparisonActualFile:
    file_ref = parse_file_ref.parse_file_ref_from_token_parser(ACTUAL_RELATIVITY_CONFIGURATION,
                                                               token_parser)
    return ActComparisonActualFileForFileRef(file_ref)


_MAIN_DESCRIPTION_REST = """\
FAILs if {checked_file} is not an existing regular file.
"""
