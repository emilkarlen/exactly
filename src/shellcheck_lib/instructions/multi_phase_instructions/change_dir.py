import enum
import os
import pathlib

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string, ensure_is_not_option_argument

DESCRIPTION = Description(
    'Changes current directory',
    """
    Uses Posix syntax for paths. I.e. directories are separated by /.
    """,
    [
        InvokationVariant('DIRECTORY',
                          'Changes to the given directory (paths are relative current directory).'),
        InvokationVariant('--act-root',
                          'Changes to SHELLCHECK ACT directory.'),
        InvokationVariant('--rel-tmp [DIRECTORY]',
                          'Changes to SHELLCHECK TMP directory, or a given sub directory of it.'),
    ])

TMP_OPTION = '--rel-tmp'
ACT_OPTION = '--act-root'

SYNTAX_DESCRIPTION = 'Usage: [--rel-tmp] [DIRECTORY]'


class DestinationType(enum.Enum):
    ACT_DIR = 0
    REL_TMP_DIR = 1
    REL_CWD = 2


class DestinationDirectory(tuple):
    def __new__(cls,
                destination_type: DestinationType,
                directory_argument: pathlib.PurePath):
        return tuple.__new__(cls, (destination_type, directory_argument))

    @property
    def destination_type(self) -> DestinationType:
        return self[0]

    @property
    def directory_argument(self) -> pathlib.PurePath:
        return self[1]


def parse(argument: str) -> DestinationDirectory:
    arguments = spit_arguments_list_string(argument)

    if not arguments:
        raise SingleInstructionInvalidArgumentException('Missing arguments.')
    if arguments[0] == ACT_OPTION:
        if len(arguments) != 1:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments to {}: {}'.format(ACT_OPTION,
                                                                                                     str(arguments)))
        return DestinationDirectory(DestinationType.ACT_DIR, None)
    if arguments[0] == TMP_OPTION:
        del arguments[0]
        num_arguments = len(arguments)
        if num_arguments == 0:
            return DestinationDirectory(DestinationType.REL_TMP_DIR, pathlib.PurePosixPath())
        if num_arguments == 1:
            ensure_is_not_option_argument(arguments[0])
            return DestinationDirectory(DestinationType.REL_TMP_DIR, pathlib.PurePosixPath(arguments[0]))
        raise SingleInstructionInvalidArgumentException('Invalid arguments of {}: {}'.format(TMP_OPTION,
                                                                                             str(arguments)))
    else:
        num_arguments = len(arguments)
        if num_arguments == 1:
            ensure_is_not_option_argument(arguments[0])
            return DestinationDirectory(DestinationType.REL_CWD, pathlib.PurePosixPath(arguments[0]))
        raise SingleInstructionInvalidArgumentException('Invalid arguments: {}'.format(str(arguments)))

        #
        # if len(arguments) != 1:
        #     raise SingleInstructionInvalidArgumentException(SYNTAX_DESCRIPTION)
        # argument = arguments[0]
        # if is_option_argument(argument):
        #     if argument != TMP_OPTION:
        #         raise SingleInstructionInvalidArgumentException(SYNTAX_DESCRIPTION)
        #     return DestinationDirectory(DestinationType.REL_TMP_DIR, None)
        # argument_path = pathlib.PurePosixPath(argument)
        # return DestinationDirectory(DestinationType.REL_CWD, argument_path)
        #


def change_dir(destination: DestinationDirectory,
               eds: ExecutionDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = _destination_path(destination, eds)
    try:
        os.chdir(str(dir_path))
    except FileNotFoundError:
        return 'Directory does not exist: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Not a directory: {}'.format(dir_path)
    return None


def _destination_path(destination: DestinationDirectory,
                      eds: ExecutionDirectoryStructure) -> pathlib.Path:
    if destination.destination_type is DestinationType.ACT_DIR:
        return eds.act_dir
    elif destination.destination_type is DestinationType.REL_TMP_DIR:
        return eds.tmp.user_dir / destination.directory_argument
    else:
        return pathlib.Path.cwd() / destination.directory_argument
