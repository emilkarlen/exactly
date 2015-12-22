import os

from shellcheck_lib.instructions.utils.destination_path import *
from shellcheck_lib.instructions.utils.parse_utils import spit_arguments_list_string
from shellcheck_lib.test_case.help.instruction_description import InvokationVariant, DescriptionWithConstantValues, \
    Description


def DESCRIPTION(instruction_name: str) -> Description:
    return DescriptionWithConstantValues(
            'Changes Present Working Directory',
            """
            Uses Posix syntax for paths. I.e. directories are separated by /.
            """,
            [
                InvokationVariant('[{}] [DIRECTORY]'.format('|'.join(OPTIONS)),
                                  'Changes to the given directory (paths are relative present directory).'),
                InvokationVariant('{} [DIRECTORY]'.format(REL_ACT_OPTION),
                                  'Changes to a directory relative the SHELLCHECK ACT directory.'),
                InvokationVariant('{} [DIRECTORY]'.format(REL_TMP_OPTION),
                                  'Changes to a directory relative the SHELLCHECK TMP directory.'),
            ],
            instruction_name=instruction_name)


def parse(argument: str) -> DestinationPath:
    arguments = spit_arguments_list_string(argument)

    (destination_path, remaining_arguments) = parse_destination_path(DestinationType.REL_CWD, False, arguments)
    if remaining_arguments:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(remaining_arguments))
    return destination_path


def change_dir(destination: DestinationPath,
               eds: ExecutionDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = destination.resolved_path(eds)
    try:
        os.chdir(str(dir_path))
    except FileNotFoundError:
        return 'Directory does not exist: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Not a directory: {}'.format(dir_path)
    return None
