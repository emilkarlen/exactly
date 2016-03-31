import os

from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from shellcheck_lib.instructions.utils.destination_path import *
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat.structure.paragraph import single_para


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Changes Present Working Directory.'

    def main_description_rest(self) -> list:
        return single_para('Uses Posix syntax for paths. I.e. directories are separated by /.')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant('[{}] [DIRECTORY]'.format('|'.join(OPTIONS)),
                              single_para('Changes to the given directory '
                                          '(paths are relative present directory).')),
            InvokationVariant('{} [DIRECTORY]'.format(REL_ACT_OPTION),
                              single_para('Changes to a directory relative the SHELLCHECK ACT directory.')),
            InvokationVariant('{} [DIRECTORY]'.format(REL_TMP_OPTION),
                              single_para('Changes to a directory relative the SHELLCHECK TMP directory.')),
        ]


def parse(argument: str) -> DestinationPath:
    arguments = split_arguments_list_string(argument)

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


def execute_with_sh_result(destination: DestinationPath,
                           eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
    error_message = change_dir(destination, eds)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
