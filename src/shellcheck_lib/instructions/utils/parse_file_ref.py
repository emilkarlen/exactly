import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import ensure_is_not_option_argument, TokenStream, is_option_argument
from shellcheck_lib.instructions.utils.relative_path_options import REL_TMP_OPTION, REL_CWD_OPTION, REL_HOME_OPTION, \
    REL_ACT_OPTION
from . import file_ref

ALL_REL_OPTIONS = (REL_HOME_OPTION, REL_CWD_OPTION, REL_TMP_OPTION)

_REL_OPTION_TO_FILE_REF_CONSTRUCTOR = {
    REL_HOME_OPTION:
        file_ref.rel_home,
    REL_CWD_OPTION:
        file_ref.rel_cwd,
    REL_ACT_OPTION:
        file_ref.rel_act,
    REL_TMP_OPTION:
        file_ref.rel_tmp_user,
}


def parse_relative_file_argument(arguments: list) -> (file_ref.FileRef, list):
    """
    If no relativity-option is specified, the file is assumed to be rel-home.

    :param arguments: All remaining arguments for the instruction.
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_two_arguments_for_option(option: str):
        if len(arguments) < 2:
            raise SingleInstructionInvalidArgumentException('{} requires a FILE argument'.format(option))

    if not arguments:
        raise SingleInstructionInvalidArgumentException('Missing file argument')
    first_argument = arguments[0]

    if is_option_argument(first_argument):
        try:
            con = _REL_OPTION_TO_FILE_REF_CONSTRUCTOR[first_argument]
        except KeyError:
            msg = 'Invalid option {}'.format(first_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        ensure_have_at_least_two_arguments_for_option(first_argument)
        return con(arguments[1]), arguments[2:]
    else:
        ensure_is_not_option_argument(first_argument)
        first_argument_path = pathlib.PurePath(first_argument)
        if first_argument_path.is_absolute():
            fr = file_ref.absolute_file_name(first_argument)
        else:
            fr = file_ref.rel_home(first_argument)
        return fr, arguments[1:]


def parse_file_ref(tokens: TokenStream,
                   argument_syntax_name: str = 'FILE') -> (file_ref.FileRef, TokenStream):
    """
    If no relativity-option is specified, the file is assumed to be rel-home.

    :param tokens: Argument list
    :param argument_syntax_name: Name of argument in error messages.
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_two_arguments_for_option(option: str) -> TokenStream:
        token1 = tokens.tail
        if token1.is_null:
            raise SingleInstructionInvalidArgumentException('{} requires a {} argument'.format(option,
                                                                                               argument_syntax_name))
        return token1

    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException('Missing {} argument'.format(argument_syntax_name))
    first_argument = tokens.head
    if is_option_argument(first_argument):
        try:
            con = _REL_OPTION_TO_FILE_REF_CONSTRUCTOR[first_argument]
        except KeyError:
            msg = 'Invalid option for reference to {}: {}'.format(argument_syntax_name,
                                                                  first_argument)
            raise SingleInstructionInvalidArgumentException(msg)
        tokens1 = ensure_have_at_least_two_arguments_for_option(first_argument)
        return con(tokens1.head), tokens1.tail
    else:
        first_argument_path = pathlib.PurePath(first_argument)
        if first_argument_path.is_absolute():
            fr = file_ref.absolute_file_name(first_argument)
        else:
            fr = file_ref.rel_home(first_argument)
        return fr, tokens.tail


def parse_non_home_file_ref(arguments: list) -> (file_ref.FileRef, list):
    """
    Default (i.e. when no option is given) is Relative CWD.
    :param arguments: Argument list, with first arguments being those that are
    supposed to specify a FileRef.
    :return: (FileRef, arguments remaining after file argument)
    """

    def ensure_have_at_least_two_arguments_for_option(option: str):
        if len(arguments) < 2:
            raise SingleInstructionInvalidArgumentException('{} requires a FILE argument'.format(option))

    first_argument = arguments[0]
    if first_argument == REL_CWD_OPTION:
        ensure_have_at_least_two_arguments_for_option(REL_CWD_OPTION)
        return file_ref.rel_cwd(arguments[1]), arguments[2:]
    elif first_argument == REL_TMP_OPTION:
        ensure_have_at_least_two_arguments_for_option(REL_TMP_OPTION)
        return file_ref.rel_tmp_user(arguments[1]), arguments[2:]
    else:
        ensure_is_not_option_argument(first_argument)
        return file_ref.rel_cwd(first_argument), arguments[1:]
