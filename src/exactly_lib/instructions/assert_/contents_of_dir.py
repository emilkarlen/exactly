import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.test_case.instructions.assign_symbol import ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT, \
    EMPTY_ARGUMENT_CONSTANT
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.parse.token_stream_parse import new_token_parser
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
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'checked_file': _PATH_ARGUMENT.name,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    _PATH_ARGUMENT)
        self.relativity_of_actual_arg = a.Named('RELATIVITY')
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               self.relativity_of_actual_arg)

    def single_line_description(self) -> str:
        return _SINGLE_LINE_DESCRIPTION

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        # negation_arguments = [negation_of_assertion.optional_negation_argument_usage()]
        arguments = [self.actual_file, mandatory_empty_arg]

        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              self._paragraphs(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)),
        ]

    def syntax_element_descriptions(self) -> list:
        mandatory_actual_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                                     path_syntax.PATH_ARGUMENT)
        actual_file_arg_sed = SyntaxElementDescription(
            _PATH_ARGUMENT.name,
            self._paragraphs(
                _PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [self.actual_file_relativity,
                     mandatory_actual_path]
                ),
                rel_opts.default_relativity_for_rel_opt_type(
                    path_syntax.PATH_ARGUMENT.name,
                    ACTUAL_RELATIVITY_CONFIGURATION.options.default_option))]
        )

        relativity_of_actual_file_sed = rel_opts.relativity_syntax_element_description(
            path_syntax.PATH_ARGUMENT,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            self.relativity_of_actual_arg)

        return [actual_file_arg_sed,
                relativity_of_actual_file_sed]

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(ACTUAL_RELATIVITY_CONFIGURATION.options)
        refs = rel_path_doc.cross_refs_for_concepts(concepts)
        refs.append(ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE)
        return refs

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
        return self._path_to_check.references

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
            raise pfh_ex_method.PfhFailException(self._error_message(num_files_in_dir, files_in_dir))

    def _error_message(self, num_files_in_dir: int, actual_files_in_dir: list) -> str:
        first_line = 'Directory is not empty. It contains {} files.'.format(str(num_files_in_dir))
        dir_contents_lines = self._dir_contents_err_msg_lines(actual_files_in_dir)
        ret_val = '\n'.join([first_line,
                             '',
                             'Actual contents:'] +
                            dir_contents_lines)
        return ret_val

    @staticmethod
    def _dir_contents_err_msg_lines(actual_files_in_dir: list) -> list:
        if len(actual_files_in_dir) < 50:
            actual_files_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            actual_file.name
            for actual_file in actual_files_in_dir[:num_files_to_display]
        ]
        if len(actual_files_in_dir) > num_files_to_display:
            ret_val.append('...')
        return ret_val


_PATH_ARGUMENT = a.Named('PATH')

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_CWD,
            RelOptionType.REL_HOME_ACT,
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)

_SINGLE_LINE_DESCRIPTION = 'Tests the contents of a directory'

_MAIN_DESCRIPTION_REST = """\
FAIL if {checked_file} is not an existing directory.


Symbolic links are followed.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that {checked_file} is an empty directory.
"""

_PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT = "The file who's contents is checked."
