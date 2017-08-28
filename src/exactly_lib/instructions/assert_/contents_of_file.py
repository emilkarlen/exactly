from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile, \
    ActComparisonActualFileForFileRef
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration, parse_file_ref
from exactly_lib.test_case_utils.parse.parse_lines_transformer import WITH_REPLACED_ENV_VARS_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.actual_file_arg = a.Named('ACTUAL-PATH')
        super().__init__(name, {
            'checked_file': self.actual_file_arg.name,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    self.actual_file_arg)
        self._help_parts = FileContentsHelpParts(name,
                                                 self.actual_file_arg.name,
                                                 [self.actual_file])
        self.with_replaced_env_vars_option = a.Option(WITH_REPLACED_ENV_VARS_OPTION_NAME)
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
                                                                     path_syntax.PATH_ARGUMENT)
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
                    path_syntax.PATH_ARGUMENT.name,
                    ACTUAL_RELATIVITY_CONFIGURATION.options.default_option))]
        )

        relativity_of_actual_file_seds = rel_opts.relativity_syntax_element_descriptions(
            path_syntax.PATH_ARGUMENT,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            relativity_of_actual_arg)

        return (self._help_parts.syntax_element_descriptions_at_top() +
                [actual_file_arg_sed] +
                relativity_of_actual_file_seds +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_items(self) -> list:
        return self._help_parts.see_also_items()


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        source.consume_initial_space_on_current_line()
        if source.is_at_eol:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (FILE)')
        comparison_target = parse_actual_file_argument(source)
        source.consume_initial_space_on_current_line()
        instruction = parsing.parse_comparison_operation(comparison_target,
                                                         source)
        return instruction


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
