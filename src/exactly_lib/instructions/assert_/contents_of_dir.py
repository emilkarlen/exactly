import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile, \
    ActComparisonActualFileForFileRef
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.parse.token_stream_parse import new_token_parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.parse import rel_opts_configuration, parse_file_ref
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
            instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME)
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               a.Named('ACTUAL-REL'))

    def single_line_description(self) -> str:
        return 'Tests the contents of a directory'

    def main_description_rest(self) -> list:
        return self._paragraphs("""\
        FAILs if {checked_file} is not an existing directory.
        """)

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

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

    def _cls(self, additional_argument_usages: list) -> str:
        return self._cl_syntax_for_args([self.actual_file] + additional_argument_usages)


class Parser(InstructionParserThatConsumesCurrentLine):
    def __init__(self):
        self.format_map = {
            'PATH': _PATH_ARGUMENT.name,
        }

    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        tokens = new_token_parser(rest_of_line,
                                  self.format_map)
        path_to_check = tokens.consume_file_ref(ACTUAL_RELATIVITY_CONFIGURATION)
        tokens.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(EMPTINESS_CHECK_ARGUMENT)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return _Instruction(path_to_check)


class _Instruction(AssertPhaseInstruction):
    def __init__(self, path_to_check: FileRefResolver):
        self._path_to_check = path_to_check

    def symbol_usages(self) -> list:
        return []  # TODO this is wrong, fix by adding tests!

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        emptiness_checker = _EmptinessChecker(self._path_to_check)
        return pfh_ex_method.translate_pfh_exception_to_pfh(emptiness_checker.main,
                                                            environment)


class _EmptinessChecker:
    def __init__(self, path_to_check: FileRefResolver):
        self._path_to_check = path_to_check

    def main(self, environment: InstructionEnvironmentForPostSdsStep):
        self._fail_if_path_does_not_exist_as_a_dir(environment)
        self._fail_if_path_dir_is_not_empty(environment)

    def _fail_if_path_does_not_exist_as_a_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)
        failure_message = file_ref_check.pre_or_post_sds_failure_message_or_none(
            file_ref_check.FileRefCheck(self._path_to_check,
                                        expect_existing_dir),
            environment.path_resolving_environment_pre_or_post_sds)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)

    def _fail_if_path_dir_is_not_empty(self, environment: InstructionEnvironmentForPostSdsStep):
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self._path_to_check.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        files_in_dir = list(path_to_check.iterdir())
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir != 0:
            raise pfh_ex_method.PfhFailException('Number of files in dir: ' + str(num_files_in_dir))


_PATH_ARGUMENT = a.Named('PATH')

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
            RelOptionType.REL_CWD,
            RelOptionType.REL_HOME_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)


def parse_actual_file_argument(source: ParseSource) -> ComparisonActualFile:
    file_ref = parse_file_ref.parse_file_ref_from_parse_source(source,
                                                               ACTUAL_RELATIVITY_CONFIGURATION)
    return ActComparisonActualFileForFileRef(file_ref)
