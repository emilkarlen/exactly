import functools
import pathlib
import types

from exactly_lib.help_texts.argument_rendering import path_syntax
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
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsStringSymbolReference, \
    PathPartResolverAsFixedPath, PathPartResolverAsNothing
from exactly_lib.symbol.value_structure import SymbolReference
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.parse.token import TokenType, Token
from exactly_lib.util.symbol_table import SymbolTable

ALL_REL_OPTIONS = set(RelOptionType) - {RelOptionType.REL_RESULT}

ALL_REL_OPTION_VARIANTS = PathRelativityVariants(ALL_REL_OPTIONS, True)

ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX = ALL_REL_OPTIONS - {RelOptionType.REL_HOME}

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    False)

ALL_REL_OPTION_VARIANTS_WITH_TARGETS_INSIDE_SANDBOX_OR_ABSOLUTE = PathRelativityVariants(
    ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    True)


def all_rel_options_config(argument_syntax_name: str,
                           path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(PathRelativityVariants(ALL_REL_OPTIONS, True),
                                                                  True,
                                                                  RelOptionType.REL_HOME),
                                          argument_syntax_name,
                                          path_suffix_is_required)


ALL_REL_OPTIONS_CONFIG = all_rel_options_config(path_syntax.PATH_SYNTAX_ELEMENT_NAME)

STANDARD_NON_HOME_RELATIVITY_VARIANTS = PathRelativityVariants(
    ALL_REL_OPTIONS - {RelOptionType.REL_HOME},
    True)

STANDARD_NON_HOME_OPTIONS = RelOptionsConfiguration(STANDARD_NON_HOME_RELATIVITY_VARIANTS,
                                                    True,
                                                    RelOptionType.REL_CWD)


def non_home_config(argument_syntax_name: str,
                    path_suffix_is_required: bool = True) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(STANDARD_NON_HOME_OPTIONS,
                                          argument_syntax_name,
                                          path_suffix_is_required)


NON_HOME_CONFIG = non_home_config(path_syntax.PATH_SYNTAX_ELEMENT_NAME)


def parse_file_ref_from_parse_source(source: ParseSource,
                                     conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param source: Has a current line
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: If cannot parse a FileRef
    """

    ts = TokenStream2(source.remaining_part_of_current_line)
    ret_val = parse_file_ref(ts, conf)
    source.consume(ts.position)
    return ret_val


def parse_file_ref(tokens: TokenStream2,
                   conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    """
    :param tokens: Argument list
    :return: The parsed FileRef, remaining arguments after file was parsed.
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    def result_from_no_arguments() -> FileRefResolver:
        return FileRefConstant(file_refs.of_rel_option(conf.options.default_option,
                                                       PathPartAsNothing()))

    if tokens.is_null:
        if conf.path_suffix_is_required:
            _raise_missing_arguments_exception(conf)
        else:
            return result_from_no_arguments()

    initial_argument_string = tokens.remaining_part_of_current_line
    relativity_info = parse_explicit_relativity_info(conf.options, tokens)
    if tokens.is_null:
        if conf.path_suffix_is_required:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(conf.argument_syntax_name,
                                                 initial_argument_string))
        else:
            if relativity_info is None:
                return result_from_no_arguments()
            else:
                path_part_resolver2_file_ref_resolver = _file_ref_constructor(relativity_info)
                return path_part_resolver2_file_ref_resolver(PathPartResolverAsNothing())

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
        path_suffix = PathPartResolverAsStringSymbolReference(symbol_name_of_symbol_reference)
        return path_part_2_file_ref_resolver(path_suffix)
    else:
        path_argument_str = path_argument_token.string
        path_argument_path = pathlib.PurePath(path_argument_str)
        if path_argument_path.is_absolute():
            return FileRefConstant(file_refs.absolute_file_name(path_argument_str))
    path_suffix = PathPartResolverAsFixedPath(path_argument_str)
    return path_part_2_file_ref_resolver(path_suffix)


def _just_string_argument(argument: str,
                          conf: RelOptionArgumentConfiguration) -> FileRefResolver:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        return FileRefConstant(file_refs.absolute_file_name(argument))
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
    :rtype PathPartResolver -> FileRefResolver: 
    """
    if isinstance(relativity_info, RelOptionType):
        return lambda path_suffix_resolver: _FileRefResolverOfRelativityOptionAndSuffixResolver(relativity_info,
                                                                                                path_suffix_resolver)
    elif isinstance(relativity_info, SymbolReference):
        return functools.partial(rel_symbol, relativity_info)
    else:
        raise TypeError("You promised you shouldn't give me a  " + str(relativity_info))


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
    def references(self) -> list:
        return self.path_suffix_resolver.references
