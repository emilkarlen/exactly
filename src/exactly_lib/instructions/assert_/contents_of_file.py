from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ActComparisonActualFileForFileRef
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration, parse_file_ref
from exactly_lib.util.cli_syntax.elements import argument as a

ACTUAL_PATH_ARGUMENT = a.Named('ACTUAL-PATH')


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.actual_file_arg = ACTUAL_PATH_ARGUMENT
        super().__init__(name, {
            'checked_file': self.actual_file_arg.name,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    self.actual_file_arg)
        self._help_parts = FileContentsHelpParts(name,
                                                 self.actual_file_arg.name,
                                                 [self.actual_file])
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               a.Named('ACTUAL-REL'))

    def single_line_description(self) -> str:
        return 'Tests the contents of a file'

    def main_description_rest(self) -> list:
        return self._paragraphs("""\
        FAILs if {checked_file} is not an existing regular file.
        """)

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

    def _cls(self, additional_argument_usages: list) -> str:
        return self._cl_syntax_for_args([self.actual_file] + additional_argument_usages)

    def syntax_element_descriptions(self) -> list:
        mandatory_actual_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                                     instruction_arguments.PATH_ARGUMENT)
        relativity_of_actual_arg = a.Named('RELATIVITY-OF-ACTUAL-PATH')
        optional_relativity_of_actual = a.Single(a.Multiplicity.OPTIONAL,
                                                 relativity_of_actual_arg)
        actual_file_arg_sed = SyntaxElementDescription(
            self.actual_file_arg.name,
            self._paragraphs(
                "The file who's contents is checked."),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [optional_relativity_of_actual,
                     mandatory_actual_path]),
                rel_opts.default_relativity_for_rel_opt_type(
                    instruction_arguments.PATH_ARGUMENT.name,
                    ACTUAL_RELATIVITY_CONFIGURATION.options.default_option))]
        )

        relativity_of_actual_file_seds = rel_opts.relativity_syntax_element_descriptions(
            instruction_arguments.PATH_ARGUMENT,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            relativity_of_actual_arg)

        return (self._help_parts.syntax_element_descriptions_at_top() +
                [actual_file_arg_sed] +
                relativity_of_actual_file_seds +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_set(self) -> SeeAlsoSet:
        return self._help_parts.see_also_set()


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parse_prime.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parse_prime.TokenParserPrime), 'Must have a TokenParser'  # Type info for IDE
            token_parser.require_is_not_at_eol(
                'Missing {actual_file} argument'.format(actual_file=ACTUAL_PATH_ARGUMENT.name))

            comparison_target = parse_actual_file_argument_from_token_parser(token_parser)
            token_parser.require_is_not_at_eol('Missing file comparison argument')
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


def parse_actual_file_argument_from_token_parser(token_parser: token_stream_parse_prime.TokenParserPrime
                                                 ) -> ComparisonActualFile:
    file_ref = parse_file_ref.parse_file_ref_from_token_parser(ACTUAL_RELATIVITY_CONFIGURATION,
                                                               token_parser)
    return ActComparisonActualFileForFileRef(file_ref)
