import functools
import pathlib

import types

from exactly_lib.instructions.utils.arg_parse.file_ref_from_symbol_reference import \
    _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix
from exactly_lib.instructions.utils.arg_parse.parse_relativity_util import parse_explicit_relativity_info
from exactly_lib.instructions.utils.arg_parse.parse_utils import ensure_is_not_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.instructions.utils.arg_parse.symbol import parse_symbol_reference
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import TokenType, Token
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsStringSymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.value_definition.concrete_values import FileRefResolver
from exactly_lib.value_definition.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_resolvers.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_structure import ValueReference

ALL_REL_OPTIONS = set(RelOptionType) - {RelOptionType.REL_RESULT}

ALL_REL_OPTION_VARIANTS = PathRelativityVariants(ALL_REL_OPTIONS, True)

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {RelOptionType.REL_HOME}

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    False)


def all_rel_options_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(PathRelativityVariants(ALL_REL_OPTIONS, True),
                                                                  True,
                                                                  RelOptionType.REL_HOME),
                                          argument_syntax_name)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config('FILE')

STANDARD_NON_HOME_RELATIVITY_VARIANTS = PathRelativityVariants(
    ALL_REL_OPTIONS - {RelOptionType.REL_HOME},
    True)

STANDARD_NON_HOME_OPTIONS = RelOptionsConfiguration(STANDARD_NON_HOME_RELATIVITY_VARIANTS,
                                                    True,
                                                    RelOptionType.REL_CWD)


def non_home_config(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HOME_OPTIONS,
                                          argument_syntax_name)


NON_HOME_CONFIG = non_home_config('FILE')


def parse_file_ref_from_parse_source(source: ParseSource, conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param source: Has a current line
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    ts = TokenStream2(source.remaining_part_of_current_line)
    ret_val = parse_file_ref(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_file_ref(tokens: TokenStream2, conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param tokens: Argument list
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    if tokens.is_null:
        _raise_missing_arguments_exception(conf)

    initial_argument_string = tokens.remaining_part_of_current_line
    relativity_info = parse_explicit_relativity_info(conf.options, tokens)
    if tokens.is_null:
        raise SingleInstructionInvalidArgumentException(
            'Missing {} argument: {}'.format(conf.argument_syntax_name,
                                             initial_argument_string))
    token = tokens.consume()
    if token.type is TokenType.PLAIN:
        ensure_is_not_option_argument(token.string)
    if relativity_info is None:
        return _without_explicit_relativity(token, conf)
    else:
        path_part_2_file_ref_resolver = _file_ref_constructor(relativity_info)
        return _with_explicit_relativity(token, path_part_2_file_ref_resolver)


def _without_explicit_relativity(path_argument: Token, conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    symbol_name_of_symbol_reference = parse_symbol_reference(path_argument)
    if symbol_name_of_symbol_reference is None:
        return _just_string_argument(path_argument.string, conf)
    else:
        return _just_symbol_reference_argument(symbol_name_of_symbol_reference, conf)


def _with_explicit_relativity(path_argument_token: Token,
                              path_part_2_file_ref_resolver: types.FunctionType) -> FileRefResolver:
    symbol_name_of_symbol_reference = parse_symbol_reference(path_argument_token)
    if symbol_name_of_symbol_reference:
        path_suffix = PathPartAsStringSymbolReference(symbol_name_of_symbol_reference)
        return path_part_2_file_ref_resolver(path_suffix)
    else:
        path_argument_str = path_argument_token.string
        path_argument_path = pathlib.PurePath(path_argument_str)
        if path_argument_path.is_absolute():
            return FileRefConstant(file_refs.absolute_file_name(path_argument_str))
    path_suffix = PathPartAsFixedPath(path_argument_str)
    return path_part_2_file_ref_resolver(path_suffix)


def _just_string_argument(argument: str,
                          conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    path_suffix = PathPartAsFixedPath(argument)
    return FileRefConstant(file_refs.of_rel_option(conf.options.default_option, path_suffix))


def _just_symbol_reference_argument(symbol_name: str,
                                    conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    return _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix(
        symbol_name,
        conf.options.default_option,
        conf.options.accepted_relativity_variants)


def _raise_missing_arguments_exception(conf: RelOptionArgumentConfiguration):
    msg = 'Missing %s argument' % conf.argument_syntax_name
    raise SingleInstructionInvalidArgumentException(msg)


def _file_ref_constructor(relativity_info) -> types.FunctionType:
    """
    :rtype PathPart -> FileRefResolver: 
    """
    if isinstance(relativity_info, RelOptionType):
        return lambda path_suffix: FileRefConstant(file_refs.of_rel_option(relativity_info, path_suffix))
    elif isinstance(relativity_info, ValueReference):
        return functools.partial(rel_value_definition, relativity_info)
    else:
        raise TypeError("You promised you shouldn't give me a  " + str(relativity_info))
