import pathlib
import types

import exactly_lib.test_case.file_refs
from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream, is_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import TokenType, Token
from exactly_lib.section_document.parser_implementations.token_parse import parse_token_or_none_on_current_line
from exactly_lib.test_case import file_ref
from exactly_lib.test_case import file_refs
from exactly_lib.util.cli_syntax import option_parsing

_REL_OPTION_2_FILE_REF_CONSTRUCTOR = {
    rel_opts.RelOptionType.REL_HOME: exactly_lib.test_case.file_refs.rel_home,
    rel_opts.RelOptionType.REL_CWD: exactly_lib.test_case.file_refs.rel_cwd,
    rel_opts.RelOptionType.REL_ACT: exactly_lib.test_case.file_refs.rel_act,
    rel_opts.RelOptionType.REL_TMP: exactly_lib.test_case.file_refs.rel_tmp_user,
}

ALL_REL_OPTIONS = set(rel_opts.RelOptionType) - {rel_opts.RelOptionType.REL_RESULT}

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {rel_opts.RelOptionType.REL_HOME}


def all_rel_options_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(ALL_REL_OPTIONS,
                                                                  rel_opts.RelOptionType.REL_HOME),
                                          argument_syntax_name)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config('FILE')

DEFAULT_CONFIG = ALL_REL_OPTIONS_CONFIG

STANDARD_NON_HOME_OPTIONS = RelOptionsConfiguration(ALL_REL_OPTIONS - {rel_opts.RelOptionType.REL_HOME},
                                                    rel_opts.RelOptionType.REL_CWD)


def non_home_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HOME_OPTIONS,
                                          argument_syntax_name)


NON_HOME_CONFIG = non_home_config('FILE')


REL_VALUE_DEFINITION_OPTION = '--rel'
VALUE_DEFINITION = 'value definition'
REL_VALUE_DEFINITION_OPTION_ARGUMENT = 'VALUE-NAME'


def _is_rel_variable_definition_option(option: str) -> bool:
    return REL_VALUE_DEFINITION_OPTION == option


def parse_file_ref_from_parse_source(source: ParseSource,
                                     conf: RelOptionArgumentConfiguration = DEFAULT_CONFIG) -> file_ref.FileRef:
    """
    :param source: Has a current line
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    def ensure_have_at_least_one_more_argument_for_option(option: str) -> Token:
        token1 = parse_token_or_none_on_current_line(source)
        if token1 is None:
            _raise_missing_option_argument_exception(option, conf)
        return token1

    first_argument = parse_token_or_none_on_current_line(source)
    if first_argument is None:
        _raise_missing_arguments_exception(conf)

    if first_argument.type is TokenType.PLAIN and is_option_argument(first_argument.string):
        if _is_rel_variable_definition_option(first_argument.string):
            value_definition_name = parse_token_or_none_on_current_line(source)
            if value_definition_name is None:
                error_msg = 'Missing {} argument for {} option'.format(VALUE_DEFINITION, REL_VALUE_DEFINITION_OPTION)
                raise SingleInstructionInvalidArgumentException(error_msg)
            file_path_arg = ensure_have_at_least_one_more_argument_for_option(
                '{} {}'.format(REL_VALUE_DEFINITION_OPTION,
                               REL_VALUE_DEFINITION_OPTION_ARGUMENT))
            return file_refs.rel_value_definition(file_path_arg.string, value_definition_name.string)
        else:
            file_ref_constructor = _get_file_ref_constructor(first_argument.string, conf)
            tokens1 = ensure_have_at_least_one_more_argument_for_option(first_argument.string)
            return file_ref_constructor(tokens1.string)
    else:
        return _read_absolute_or_default_file_ref(first_argument.string, conf)


def parse_file_ref(tokens: TokenStream,
                   conf: RelOptionArgumentConfiguration = DEFAULT_CONFIG) -> (file_ref.FileRef, TokenStream):
    """
    :param tokens: Argument list
    :return: The parsed FileRef, remaining arguments after file was parsed.
    """

    def ensure_have_at_least_two_arguments_for_option(option: str) -> TokenStream:
        token1 = tokens.tail
        if token1.is_null:
            _raise_missing_option_argument_exception(option, conf)
        return token1

    if tokens.is_null:
        _raise_missing_arguments_exception(conf)

    first_argument = tokens.head
    if is_option_argument(first_argument):
        file_ref_constructor = _get_file_ref_constructor(first_argument, conf)
        tokens1 = ensure_have_at_least_two_arguments_for_option(first_argument)
        return file_ref_constructor(tokens1.head), tokens1.tail
    else:
        fr = _read_absolute_or_default_file_ref(first_argument, conf)
        return fr, tokens.tail


def _read_absolute_or_default_file_ref(argument: str,
                                       conf: RelOptionArgumentConfiguration) -> file_ref.FileRef:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        return exactly_lib.test_case.file_refs.absolute_file_name(argument)
    else:
        file_ref_constructor = _REL_OPTION_2_FILE_REF_CONSTRUCTOR[conf.options.default_option]
        return file_ref_constructor(argument)


def _get_file_ref_constructor(option_argument: str,
                              conf: RelOptionArgumentConfiguration) -> types.FunctionType:
    for relativity_type in conf.options.accepted_options:
        option_name = rel_opts.REL_OPTIONS_MAP[relativity_type].option_name
        if option_parsing.matches(option_name, option_argument):
            return _REL_OPTION_2_FILE_REF_CONSTRUCTOR[relativity_type]
    msg = 'Invalid option for reference to %s: %s' % (conf.argument_syntax_name, option_argument)
    raise SingleInstructionInvalidArgumentException(msg)


def _raise_missing_option_argument_exception(option: str,
                                             conf: RelOptionArgumentConfiguration):
    _msg = '{} requires a {} argument'.format(option, conf.argument_syntax_name)
    raise SingleInstructionInvalidArgumentException(_msg)


def _raise_missing_arguments_exception(conf: RelOptionArgumentConfiguration):
    msg = 'Missing %s argument' % conf.argument_syntax_name
    raise SingleInstructionInvalidArgumentException(msg)
