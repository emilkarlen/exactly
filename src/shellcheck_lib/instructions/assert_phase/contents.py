import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.execution_directory_structure import \
    root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars, SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR, \
    SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR
from shellcheck_lib.instructions.assert_phase.utils.contents_utils import ActualFileTransformer, EMPTY_ARGUMENT, \
    WITH_REPLACED_ENV_VARS_OPTION, parse_actual_file_argument
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_TMP_OPTION, REL_CWD_OPTION
from shellcheck_lib.test_case.instruction_documentation import InvokationVariant, InstructionReference
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.phases.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.util.textformat import parse as text_parse
from shellcheck_lib.util.textformat.structure.paragraph import single_para
from .utils import contents_utils


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionReference(instruction_name))


class TheInstructionReference(InstructionReference):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Test the contents of a file.'

    def main_description_rest(self) -> list:
        text = """\
            {} replaces all occurrences of any of the shellcheck environment variables to the name of the variable.
            (Variable values are replaced with variable names.)

            These environment variables are:

            {}.
            """.format(WITH_REPLACED_ENV_VARS_OPTION,
                       ', '.join(environment_variables.ALL_ENV_VARS))
        return text_parse.normalize_and_parse(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'FILENAME {}'.format(EMPTY_ARGUMENT),
                    single_para('File exists, is a regular file, and is empty')),
            InvokationVariant(
                    'FILENAME ! {}'.format(EMPTY_ARGUMENT),
                    single_para('File exists, is a regular file, and is not empty')),
            InvokationVariant(
                    'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                                 REL_HOME_OPTION),
                    single_para('Compares contents of FILENAME to contents of FILE '
                                '(which is a path relative home)')),
            InvokationVariant(
                    'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                                 REL_TMP_OPTION),
                    single_para('Compares contents of FILENAME to contents of FILE '
                                '(which is a path relative the shellcheck tmp directory)')),
            InvokationVariant(
                    'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                                 REL_CWD_OPTION),
                    single_para('Compares contents of FILENAME to contents of FILE '
                                '(which is a path relative current working directory)')),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (FILE)')
        (comparison_target, remaining_arguments) = parse_actual_file_argument(arguments)
        instruction = contents_utils.try_parse_content(comparison_target,
                                                       _ActualFileTransformer(),
                                                       remaining_arguments,
                                                       source)
        return instruction


class _ActualFileTransformer(ActualFileTransformer):
    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        root_dir_path = root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(environment.eds)
        if not src_file_path.is_absolute():
            src_file_path = pathlib.Path.cwd().resolve() / src_file_path
        src_file_path = src_file_path.resolve()
        return self._dst_file_path_for_absolute_src_path(environment,
                                                         root_dir_path,
                                                         src_file_path)

    @staticmethod
    def _dst_file_path_for_absolute_src_path(environment: GlobalEnvironmentForPostEdsPhase,
                                             root_dir_path: pathlib.Path,
                                             absolute_src_file_path: pathlib.Path) -> pathlib.Path:
        try:
            relative_act_dir = absolute_src_file_path.relative_to(environment.eds.act_dir)
            # path DOES reside under act_dir
            return root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR / relative_act_dir
        except ValueError:
            # path DOES NOT reside under act_dir
            return (root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR).joinpath(
                    *absolute_src_file_path.parts[1:])
