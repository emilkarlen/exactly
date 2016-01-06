import pathlib
import types

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import TokenStream, is_option_argument
from shellcheck_lib.instructions.utils.relative_path_options import REL_TMP_OPTION, REL_CWD_OPTION, REL_HOME_OPTION, \
    REL_ACT_OPTION
from . import file_ref

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

ALL_REL_OPTIONS = _REL_OPTION_TO_FILE_REF_CONSTRUCTOR.keys()


class Configuration(tuple):
    def __new__(cls,
                accepted_options,
                default_option: str,
                argument_syntax_name: str):
        return tuple.__new__(cls, (accepted_options,
                                   default_option,
                                   argument_syntax_name))

    @property
    def accepted_options(self):
        return self[0]

    @property
    def default_option(self) -> str:
        return self[1]

    @property
    def argument_syntax_name(self) -> str:
        return self[2]


DEFAULT_CONFIG = Configuration(ALL_REL_OPTIONS,
                               REL_HOME_OPTION,
                               'FILE')

NON_HOME_CONFIG = Configuration(ALL_REL_OPTIONS - {REL_HOME_OPTION},
                                REL_CWD_OPTION,
                                'FILE')


def parse_file_ref__list(arguments: list,
                         conf: Configuration = DEFAULT_CONFIG) -> (file_ref.FileRef, list):
    """
    If no relativity-option is specified, the file is assumed to be rel-home.

    :param conf:
    :param arguments: All remaining arguments for the instruction.
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_two_arguments_for_option(option: str):
        if len(arguments) < 2:
            _msg = '{} requires a {} argument'.format(option, conf.argument_syntax_name)
            raise SingleInstructionInvalidArgumentException(_msg)

    if not arguments:
        msg = 'Missing %s argument' % conf.argument_syntax_name
        raise SingleInstructionInvalidArgumentException(msg)
    first_argument = arguments[0]

    if is_option_argument(first_argument):
        file_ref_constructor = _get_file_ref_constructor(first_argument, conf)
        ensure_have_at_least_two_arguments_for_option(first_argument)
        return file_ref_constructor(arguments[1]), arguments[2:]
    else:
        fr = _read_absolute_or_default_file_ref(first_argument, conf)
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

    conf = Configuration(ALL_REL_OPTIONS,
                         REL_HOME_OPTION,
                         argument_syntax_name)

    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException('Missing {} argument'.format(argument_syntax_name))
    first_argument = tokens.head
    if is_option_argument(first_argument):
        file_ref_constructor = _get_file_ref_constructor(first_argument, conf)
        tokens1 = ensure_have_at_least_two_arguments_for_option(first_argument)
        return file_ref_constructor(tokens1.head), tokens1.tail
    else:
        fr = _read_absolute_or_default_file_ref(first_argument, conf)
        return fr, tokens.tail


def _read_absolute_or_default_file_ref(argument: str,
                                       conf: Configuration) -> file_ref.FileRef:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        return file_ref.absolute_file_name(argument)
    else:
        file_ref_constructor = _option_constructor_for(conf.default_option)
        return file_ref_constructor(argument)


def _get_file_ref_constructor(option_argument: str,
                              conf: Configuration) -> types.FunctionType:
    if option_argument not in conf.accepted_options:
        msg = 'Invalid option for reference to %s: %s' % (conf.argument_syntax_name, option_argument)
        raise SingleInstructionInvalidArgumentException(msg)
    return _option_constructor_for(option_argument)


def _option_constructor_for(relativity_option: str) -> types.FunctionType:
    try:
        return _REL_OPTION_TO_FILE_REF_CONSTRUCTOR[relativity_option]
    except KeyError:
        msg = 'parse_file_ref: Invalid relativity-option: {}'.format(relativity_option)
        raise ValueError(msg)
