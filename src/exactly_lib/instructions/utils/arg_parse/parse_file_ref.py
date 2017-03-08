import pathlib

from exactly_lib.instructions.utils import relativity_root
from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import is_option_token
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import Token
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.util.cli_syntax import option_parsing

ALL_REL_OPTIONS = set(relativity_root.RelOptionType) - {
    relativity_root.RelOptionType.REL_RESULT}

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {
    relativity_root.RelOptionType.REL_HOME}


def all_rel_options_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(ALL_REL_OPTIONS,
                                                                  True,
                                                                  relativity_root.RelOptionType.REL_HOME),
                                          argument_syntax_name)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config('FILE')

STANDARD_NON_HOME_OPTIONS = RelOptionsConfiguration(ALL_REL_OPTIONS - {
    relativity_root.RelOptionType.REL_HOME},
                                                    True,
                                                    relativity_root.RelOptionType.REL_CWD)


def non_home_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HOME_OPTIONS,
                                          argument_syntax_name)


NON_HOME_CONFIG = non_home_config('FILE')

REL_VALUE_DEFINITION_OPTION = '--rel'
VALUE_DEFINITION = 'value definition'
REL_VALUE_DEFINITION_OPTION_ARGUMENT = 'VALUE-NAME'


def _is_rel_variable_definition_option(option: str) -> bool:
    return REL_VALUE_DEFINITION_OPTION == option


def parse_file_ref_from_parse_source(source: ParseSource, conf: RelOptionArgumentConfiguration) -> FileRef:
    """
    :param source: Has a current line
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    ts = TokenStream2(source.remaining_part_of_current_line)
    ret_val = parse_file_ref(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_file_ref(tokens: TokenStream2, conf: RelOptionArgumentConfiguration) -> FileRef:
    """
    :param tokens: Argument list
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_one_more_argument_for_option(option: str) -> Token:
        tokens.consume()
        if tokens.is_null:
            _raise_missing_option_argument_exception(option, conf)
        ret_val = tokens.head
        tokens.consume()
        return ret_val

    if tokens.is_null:
        _raise_missing_arguments_exception(conf)

    first_token = tokens.head
    if is_option_token(first_token):
        root_resolver = _get_root_resolver(first_token.string, conf)
        second_token = ensure_have_at_least_one_more_argument_for_option(first_token.string)
        return file_refs.of_rel_root(root_resolver, second_token.string)
    else:
        fr = _read_absolute_or_default_file_ref(first_token.string, conf)
        tokens.consume()
        return fr


def _read_absolute_or_default_file_ref(argument: str,
                                       conf: RelOptionArgumentConfiguration) -> FileRef:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        return file_refs.absolute_file_name(argument)
    else:
        root_resolver = rel_opts.REL_OPTIONS_MAP[conf.options.default_option].root_resolver
        return file_refs.of_rel_root(root_resolver, argument)


def _get_root_resolver(option_argument: str,
                       conf: RelOptionArgumentConfiguration) -> relativity_root.RelRootResolver:
    for relativity_type in conf.options.accepted_options:
        option_name = rel_opts.REL_OPTIONS_MAP[relativity_type].option_name
        if option_parsing.matches(option_name, option_argument):
            return rel_opts.REL_OPTIONS_MAP[relativity_type].root_resolver
    msg = 'Invalid option for reference to %s: %s' % (conf.argument_syntax_name, option_argument)
    raise SingleInstructionInvalidArgumentException(msg)


def _raise_missing_option_argument_exception(option: str,
                                             conf: RelOptionArgumentConfiguration):
    _msg = '{} requires a {} argument'.format(option, conf.argument_syntax_name)
    raise SingleInstructionInvalidArgumentException(_msg)


def _raise_missing_arguments_exception(conf: RelOptionArgumentConfiguration):
    msg = 'Missing %s argument' % conf.argument_syntax_name
    raise SingleInstructionInvalidArgumentException(msg)
