import enum
import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.instructions.assert_phase.utils.contents_utils import TargetTransformer, EMPTY_ARGUMENT, \
    SOURCE_REL_HOME_OPTION, SOURCE_REL_CWD_OPTION, WITH_REPLACED_ENV_VARS_OPTION
from shellcheck_lib.test_case.os_services import OsServices
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
            'FILENAME {} FILE'.format(SOURCE_REL_HOME_OPTION),
            'Compares contents of FILENAME to contents of FILE (which is a path relative home)'),
        InvokationVariant(
            'FILENAME {} FILE'.format(SOURCE_REL_CWD_OPTION),
            'Compares contents of FILENAME to contents of FILE (which is a path relative current working directory)'),
    ])


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (file name)')
        file_argument = arguments[0]
        del arguments[0]
        comparison_target = contents_utils.ActComparisonTarget(file_argument)
        content_instruction = contents_utils.try_parse_content(comparison_target,
                                                               _TargetTransformer(),
                                                               arguments)
        if content_instruction is not None:
            return content_instruction
        raise SingleInstructionInvalidArgumentException('Invalid file instruction')


class _TargetTransformer(TargetTransformer):
    def replace_env_vars(self,
                         environment: GlobalEnvironmentForPostEdsPhase,
                         os_services: OsServices,
                         target_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('TODO: Implement env-var replacement for arbitrary file.')
