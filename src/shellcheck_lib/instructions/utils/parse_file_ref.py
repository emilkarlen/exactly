from . import file_ref
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import ensure_is_not_option_argument

SOURCE_REL_HOME_OPTION = '--rel-home'
SOURCE_REL_CWD_OPTION = '--rel-cwd'
SOURCE_REL_TMP_OPTION = '--rel-tmp'


def parse_non_act_generated_file(arguments: list) -> (file_ref.FileRef, list):
    """
    :param arguments: All remaining arguments for the instruction.
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_two_arguments_for_option(option: str):
        if len(arguments) < 2:
            raise SingleInstructionInvalidArgumentException('{} requires a FILE argument'.format(option))

    if not arguments:
        raise SingleInstructionInvalidArgumentException('Missing file argument')
    first_argument = arguments[0]
    if first_argument == SOURCE_REL_HOME_OPTION:
        ensure_have_at_least_two_arguments_for_option(SOURCE_REL_HOME_OPTION)
        return file_ref.rel_home(arguments[1]), arguments[2:]
    if first_argument == SOURCE_REL_CWD_OPTION:
        ensure_have_at_least_two_arguments_for_option(SOURCE_REL_CWD_OPTION)
        return file_ref.rel_cwd(arguments[1]), arguments[2:]
    elif first_argument == SOURCE_REL_TMP_OPTION:
        ensure_have_at_least_two_arguments_for_option(SOURCE_REL_TMP_OPTION)
        return file_ref.rel_tmp_user(arguments[1]), arguments[2:]
    else:
        ensure_is_not_option_argument(first_argument)
        return file_ref.rel_home(first_argument), arguments[1:]
