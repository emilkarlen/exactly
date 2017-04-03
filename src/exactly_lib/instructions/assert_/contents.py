import pathlib

import exactly_lib.instructions.assert_.utils.file_contents.instruction_options
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import \
    ActualFileTransformerForEnvVarsReplacementBase
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile, \
    ActComparisonActualFileForFileRef
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse import rel_opts_configuration
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import \
    root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars, SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR, \
    SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR
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
        self.with_replaced_env_vars_option = a.Option(
            exactly_lib.instructions.assert_.utils.file_contents.instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME)
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
        mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                  dt.PATH_ARGUMENT)
        relativity_of_actual_arg = a.Named('RELATIVITY-OF-ACTUAL-FILE')
        optional_relativity_of_actual = a.Single(a.Multiplicity.OPTIONAL,
                                                 relativity_of_actual_arg)
        actual_file_arg_sed = SyntaxElementDescription(
            self.actual_file_arg.name,
            self._paragraphs(
                "The file who's contents is checked."),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [optional_relativity_of_actual,
                     mandatory_path]),
                rel_opts.default_relativity_for_rel_opt_type(
                    dt.PATH_ARGUMENT.name,
                    _ACTUAL_RELATIVITY_CONFIGURATION.options.default_option))]
        )

        relativity_seds = rel_opts.relativity_syntax_element_descriptions(dt.PATH_ARGUMENT,
                                                                          _ACTUAL_RELATIVITY_CONFIGURATION.options,
                                                                          relativity_of_actual_arg)

        return [actual_file_arg_sed] + relativity_seds + self._help_parts.syntax_element_descriptions()

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
                                                         _ActualFileTransformerForEnvVarsReplacement(),
                                                         source)
        return instruction


class _ActualFileTransformerForEnvVarsReplacement(ActualFileTransformerForEnvVarsReplacementBase):
    def _dst_file_path(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        root_dir_path = root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(environment.sds)
        if not src_file_path.is_absolute():
            src_file_path = pathlib.Path.cwd().resolve() / src_file_path
        src_file_path = src_file_path.resolve()
        return self._dst_file_path_for_absolute_src_path(environment,
                                                         root_dir_path,
                                                         src_file_path)

    @staticmethod
    def _dst_file_path_for_absolute_src_path(environment: InstructionEnvironmentForPostSdsStep,
                                             root_dir_path: pathlib.Path,
                                             absolute_src_file_path: pathlib.Path) -> pathlib.Path:
        try:
            relative_act_dir = absolute_src_file_path.relative_to(environment.sds.act_dir)
            # path DOES reside under act_dir
            return root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR / relative_act_dir
        except ValueError:
            # path DOES NOT reside under act_dir
            return (root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR).joinpath(
                *absolute_src_file_path.parts[1:])


_ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(parse_file_ref.ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX,
                                                   False,  # TODO Change to true when val-defs available in assert phase
                                                   RelOptionType.REL_CWD),
    'PATH')


def parse_actual_file_argument(source: ParseSource) -> ComparisonActualFile:
    file_ref = parse_file_ref.parse_file_ref_from_parse_source(source,
                                                               _ACTUAL_RELATIVITY_CONFIGURATION)
    return ActComparisonActualFileForFileRef(file_ref)
