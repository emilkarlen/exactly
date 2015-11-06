import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.execution_directory_structure import \
    root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars, SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR, \
    SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR
from shellcheck_lib.instructions.assert_phase.utils.contents_utils import TargetTransformer, EMPTY_ARGUMENT, \
    SOURCE_REL_HOME_OPTION, SOURCE_REL_CWD_OPTION, WITH_REPLACED_ENV_VARS_OPTION, SOURCE_REL_TMP_OPTION
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from .utils import contents_utils

DESCRIPTION = Description(
    'Test the contents of a file.',
    """
    {} replaces all occurrences of any of the shellcheck environment variables to the name of the variable.
    (Variable values are replaced with variable names.)
    These environment variables are:

    {}.
    """.format(WITH_REPLACED_ENV_VARS_OPTION,
               ', '.join(environment_variables.ALL_ENV_VARS)),
    [
        InvokationVariant(
            'FILENAME {}'.format(EMPTY_ARGUMENT),
            'File exists, is a regular file, and is empty'),
        InvokationVariant(
            'FILENAME ! {}'.format(EMPTY_ARGUMENT),
            'File exists, is a regular file, and is not empty'),
        InvokationVariant(
            'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                         SOURCE_REL_HOME_OPTION),
            'Compares contents of FILENAME to contents of FILE ' +
            '(which is a path relative home)'),
        InvokationVariant(
            'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                         SOURCE_REL_TMP_OPTION),
            'Compares contents of FILENAME to contents of FILE ' +
            '(which is a path relative the shellcheck tmp directory)'),
        InvokationVariant(
            'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                         SOURCE_REL_CWD_OPTION),
            'Compares contents of FILENAME to contents of FILE ' +
            '(which is a path relative current working directory)'),
    ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (file name)')
        file_argument = arguments[0]
        file_argument_path = pathlib.Path(file_argument)
        comparison_target = contents_utils.ActComparisonTarget(file_argument)
        content_instruction = contents_utils.try_parse_content(comparison_target,
                                                               _TargetTransformer(),
                                                               arguments[1:])
        if content_instruction is not None:
            return content_instruction
        raise SingleInstructionInvalidArgumentException('Invalid file instruction')


class _TargetTransformer(TargetTransformer):
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
