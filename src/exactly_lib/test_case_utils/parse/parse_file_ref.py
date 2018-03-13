import functools
import pathlib
import types
from typing import Sequence

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.test_case.instructions import define_symbol as help_texts
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import ensure_is_not_option_argument, \
    std_error_message_text_for_token_syntax_error_from_exception, std_error_message_text_for_token_syntax_error
from exactly_lib.section_document.element_parsers.source_utils import \
    token_stream_from_remaining_part_of_current_line_of_parse_source
from exactly_lib.section_document.element_parsers.token_stream import TokenStream, TokenSyntaxError, \
    LookAheadState
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    OrReferenceRestrictions, OrRestrictionPart, string_made_up_by_just_strings
from exactly_lib.symbol.data.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.data.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.data.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.symbol.data.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath, \
    PathPartResolverAsNothing, PathPartResolverAsStringResolver
from exactly_lib.symbol.err_msg.error_messages import invalid_type_msg
from exactly_lib.symbol.err_msg.restriction_failure_renderer import error_message_for_direct_reference
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils.parse.file_ref_from_symbol_reference import \
    _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix
from exactly_lib.test_case_utils.parse.parse_relativity import parse_explicit_relativity_info
from exactly_lib.test_case_utils.parse.parse_string import parse_string_resolver_from_token, \
    parse_fragments_from_token, string_resolver_from_fragments
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.parse.token import TokenType, Token
from exactly_lib.util.symbol_table import SymbolTable

ALL_REL_OPTIONS = set(RelOptionType) - {RelOptionType.REL_RESULT}

ALL_REL_OPTION_VARIANTS = PathRelativityVariants(ALL_REL_OPTIONS, True)

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {RelOptionType.REL_HOME_CASE}

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    False)

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX_OR_ABSOLUTE = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    True)


def all_rel_options_config(argument_syntax_name: str,
                           path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(PathRelativityVariants(ALL_REL_OPTIONS, True),
                                                                  RelOptionType.REL_HOME_CASE),
                                          argument_syntax_name,
                                          path_suffix_is_required)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config(instruction_arguments.PATH_SYNTAX_ELEMENT_NAME)

STANDARD_NON_HOME_RELATIVITY_VARIANTS = PathRelativityVariants(
    ALL_REL_OPTIONS - {RelOptionType.REL_HOME_CASE},
    True)

STANDARD_NON_HOME_OPTIONS = RelOptionsConfiguration(STANDARD_NON_HOME_RELATIVITY_VARIANTS,
                                                    RelOptionType.REL_CWD)


def non_home_config(argument_syntax_name: str,
                    path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HOME_OPTIONS,
                                          argument_syntax_name,
                                          path_suffix_is_required)


NON_HOME_CONFIG = non_home_config(instruction_arguments.PATH_SYNTAX_ELEMENT_NAME)


def parse_file_ref_from_parse_source(source: ParseSource,
                                     conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param source: Has a current line
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """
    with token_stream_from_remaining_part_of_current_line_of_parse_source(source) as ts:
        return parse_file_ref(ts, conf)


def parse_file_ref_from_token_parser(conf: RelOptionArgumentConfiguration,
                                     token_parser: TokenParser
                                     ) -> FileRefResolver:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    return parse_file_ref(token_parser.token_stream, conf)


def parse_file_ref(tokens: TokenStream,
                   conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    try:
        if conf.path_suffix_is_required:
            return _parse_with_required_suffix(tokens, conf)
        else:
            return _parse_with_optional_suffix(tokens, conf)
    except TokenSyntaxError as ex:
        raise SingleInstructionInvalidArgumentException(
            std_error_message_text_for_token_syntax_error_from_exception(ex))


def _parse_with_required_suffix(tokens: TokenStream,
                                conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    if tokens.is_null:
        _raise_missing_arguments_exception(conf)
    return _parse_with_non_empty_token_stream(tokens, conf)


def _parse_with_optional_suffix(tokens: TokenStream,
                                conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    if tokens.is_null or tokens.remaining_part_of_current_line_is_empty:
        return _result_from_no_arguments(conf)
    return _parse_with_non_empty_token_stream(tokens, conf)


def _parse_with_non_empty_token_stream(tokens: TokenStream,
                                       conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    initial_argument_string = tokens.remaining_part_of_current_line
    relativity_info = parse_explicit_relativity_info(conf.options, tokens)

    if not conf.path_suffix_is_required and tokens.remaining_part_of_current_line_is_empty:
        if relativity_info is None:
            return _result_from_no_arguments(conf)
        else:
            path_part_resolver2_file_ref_resolver = _file_ref_constructor(relativity_info)
            return path_part_resolver2_file_ref_resolver(PathPartResolverAsNothing())

    if tokens.look_ahead_state is LookAheadState.NULL:
        raise SingleInstructionInvalidArgumentException(
            'Missing {} argument: {}'.format(conf.argument_syntax_name,
                                             initial_argument_string))
    elif tokens.look_ahead_state is LookAheadState.SYNTAX_ERROR:
        SingleInstructionInvalidArgumentException(
            std_error_message_text_for_token_syntax_error(tokens.head_syntax_error_description))

    token = tokens.consume()
    if token.type is TokenType.PLAIN:
        ensure_is_not_option_argument(token.string)
    if relativity_info is None:
        return _without_explicit_relativity(token, conf)
    else:
        path_part_2_file_ref_resolver = _file_ref_constructor(relativity_info)
        return _with_explicit_relativity(token, path_part_2_file_ref_resolver)


def _without_explicit_relativity(path_argument: Token, conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    string_fragments = parse_fragments_from_token(path_argument)
    if _string_fragments_is_constant(string_fragments):
        return _just_string_argument(path_argument.string, conf)
    else:
        return _just_argument_with_symbol_references(string_fragments, conf)


def _with_explicit_relativity(path_argument: Token,
                              path_part_2_file_ref_resolver: types.FunctionType) -> FileRefResolver:
    string_resolver = _parse_string_resolver(path_argument)
    if string_resolver.is_string_constant:
        path_argument_str = string_resolver.string_constant
        path_argument_path = pathlib.PurePath(path_argument_str)
        if path_argument_path.is_absolute():
            return FileRefConstant(file_refs.absolute_file_name(path_argument_str))
        path_suffix = PathPartResolverAsFixedPath(path_argument_str)
        return path_part_2_file_ref_resolver(path_suffix)
    else:
        path_suffix = PathPartResolverAsStringResolver(string_resolver)
        return path_part_2_file_ref_resolver(path_suffix)


def _just_string_argument(argument: str,
                          conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        #  TODO Should we check if absolute paths are allowed according to RelOptionArgumentConfiguration??
        return FileRefConstant(file_refs.absolute_file_name(argument))
    path_suffix = PathPartAsFixedPath(argument)
    return FileRefConstant(file_refs.of_rel_option(conf.options.default_option, path_suffix))


def _just_argument_with_symbol_references(string_fragments: list,
                                          conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    if _first_fragment_is_symbol_that_can_act_as_file_ref(string_fragments):
        file_ref_or_str_sym_ref, path_suffix = _extract_parts_that_can_act_as_file_ref_and_suffix(string_fragments,
                                                                                                  conf)
        return _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix(
            file_ref_or_str_sym_ref,
            path_suffix,
            conf.options.default_option)
    else:
        #  TODO Check if fragments represent an absolute path
        path_suffix = _path_suffix_resolver_from_fragments(string_fragments)
        return _FileRefResolverOfRelativityOptionAndSuffixResolver(conf.options.default_option,
                                                                   path_suffix)


def _result_from_no_arguments(conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    return FileRefConstant(file_refs.of_rel_option(conf.options.default_option,
                                                   PathPartAsNothing()))


def _raise_missing_arguments_exception(conf: RelOptionArgumentConfiguration):
    msg = 'Missing %s argument' % conf.argument_syntax_name
    raise SingleInstructionInvalidArgumentException(msg)


def _file_ref_constructor(relativity_info) -> types.FunctionType:
    """
    :rtype PathPartResolver -> FileRefResolver: 
    """
    if isinstance(relativity_info, RelOptionType):
        return lambda path_suffix_resolver: _FileRefResolverOfRelativityOptionAndSuffixResolver(relativity_info,
                                                                                                path_suffix_resolver)
    elif isinstance(relativity_info, SymbolReference):
        return functools.partial(rel_symbol, relativity_info)
    else:
        raise TypeError("You promised you shouldn't give me a  " + str(relativity_info))


def _extract_parts_that_can_act_as_file_ref_and_suffix(string_fragments: list,
                                                       conf: RelOptionArgumentConfiguration
                                                       ) -> (SymbolReference, PathPartResolver):
    file_ref_or_string_symbol = SymbolReference(
        string_fragments[0].value,
        path_or_string_reference_restrictions(conf.options.accepted_relativity_variants),
    )
    path_part_resolver = _path_suffix_resolver_from_fragments(string_fragments[1:])
    return file_ref_or_string_symbol, path_part_resolver


def path_or_string_reference_restrictions(accepted_relativity_variants: PathRelativityVariants):
    return OrReferenceRestrictions([
        OrRestrictionPart(
            DataValueType.PATH,
            path_relativity_restriction(accepted_relativity_variants)),
        OrRestrictionPart(
            DataValueType.STRING,
            PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
    ],
        type_must_be_either_path_or_string__err_msg_generator)


def path_relativity_restriction(accepted_relativity_variants: PathRelativityVariants):
    return ReferenceRestrictionsOnDirectAndIndirect(
        FileRefRelativityRestriction(accepted_relativity_variants))


class _FileRefResolverOfRelativityOptionAndSuffixResolver(FileRefResolver):
    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix_resolver: PathPartResolver):
        self.relativity = relativity
        self.path_suffix_resolver = path_suffix_resolver

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return file_refs.of_rel_option(self.relativity,
                                       self.path_suffix_resolver.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.path_suffix_resolver.references


def _parse_string_resolver(token: Token) -> StringResolver:
    return parse_string_resolver_from_token(token, PATH_COMPONENT_STRING_REFERENCES_RESTRICTION)


def _string_fragments_is_constant(fragments: list) -> bool:
    return len(fragments) == 1 and fragments[0].is_constant


def _first_fragment_is_symbol_that_can_act_as_file_ref(fragments: list) -> bool:
    if fragments[0].is_constant:
        return False
    if len(fragments) == 1:
        return True
    fragment2 = fragments[1]
    return fragment2.is_constant and fragment2.value.startswith('/')


def _path_suffix_resolver_from_fragments(fragments: list) -> PathPartResolver:
    if not fragments:
        return PathPartResolverAsNothing()
    string_resolver = string_resolver_from_fragments(fragments, PATH_COMPONENT_STRING_REFERENCES_RESTRICTION)
    return PathPartResolverAsStringResolver(string_resolver)


PATH_COMPONENT_STRING_REFERENCES_RESTRICTION = string_made_up_by_just_strings(
    'Every symbol used as a path component of a {path_type} '
    'must be defined as a {string_type}.'.format(
        path_type=help_texts.DATA_TYPE_INFO_DICT[DataValueType.PATH].identifier,
        string_type=help_texts.DATA_TYPE_INFO_DICT[DataValueType.STRING].identifier,
    ))


def type_must_be_either_path_or_string__err_msg_generator(name_of_failing_symbol: str,
                                                          container_of_illegal_symbol: SymbolContainer) -> str:
    value_restriction_failure = invalid_type_msg([ValueType.PATH, ValueType.STRING],
                                                 name_of_failing_symbol,
                                                 container_of_illegal_symbol)
    return '\n'.join(error_message_for_direct_reference(value_restriction_failure))
