import os

from exactly_lib.common.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from exactly_lib.execution.environment_variables import ENV_VAR_ACT, ENV_VAR_TMP
from exactly_lib.instructions.utils.destination_path import *
from exactly_lib.instructions.utils.parse_utils import split_arguments_list_string
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.textformat.structure.structures import paras


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Changes Present Working Directory.'

    def main_description_rest(self) -> list:
        return paras('Uses Posix syntax for paths. I.e. directories are separated by /.')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant('[{}] [DIRECTORY]'.format('|'.join(OPTIONS)),
                              paras('Changes to the given directory '
                                    '(paths are relative present directory).')),
            InvokationVariant('{} [DIRECTORY]'.format(REL_ACT_OPTION),
                              paras('Changes to a directory relative the %s directory.'
                                    % ENV_VAR_ACT)),
            InvokationVariant('{} [DIRECTORY]'.format(REL_TMP_OPTION),
                              paras('Changes to a directory relative the %s directory.'
                                    % ENV_VAR_TMP)),
        ]

    def see_also(self) -> list:
        from exactly_lib.help.concepts.plain_concepts.sandbox import \
            SANDBOX_CONCEPT
        return [SANDBOX_CONCEPT.cross_reference_target()]


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
