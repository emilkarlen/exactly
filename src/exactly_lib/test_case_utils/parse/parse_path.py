import functools
import pathlib
from typing import Sequence, Optional, Callable, Union

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import ensure_is_not_option_argument, \
    std_error_message_text_for_token_syntax_error_from_exception, std_error_message_text_for_token_syntax_error
from exactly_lib.section_document.element_parsers.source_utils import \
    token_stream_from_remaining_part_of_current_line_of_parse_source
from exactly_lib.section_document.element_parsers.token_stream import TokenStream, TokenSyntaxError, \
    LookAheadState
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import path_sdvs, path_part_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv, PathPartSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    OrReferenceRestrictions, OrRestrictionPart, string_made_up_by_just_strings
from exactly_lib.symbol.data.restrictions.value_restrictions import PathRelativityRestriction
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.err_msg.error_messages import invalid_type_msg
from exactly_lib.symbol.err_msg.restriction_failures import ErrorMessageForDirectReference
from exactly_lib.symbol.restriction import DataTypeReferenceRestrictions
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils.parse.parse_relativity import parse_explicit_relativity_info
from exactly_lib.test_case_utils.parse.parse_string import parse_string_sdv_from_token, \
    parse_fragments_from_token, string_sdv_from_fragments
from exactly_lib.test_case_utils.parse.path_from_symbol_reference import \
    _SdvThatIsIdenticalToReferencedPathOrWithStringValueAsSuffix
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.parse.token import TokenType, Token
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


def parse_path_from_parse_source(source: ParseSource,
                                 conf: RelOptionArgumentConfiguration) -> PathSdv:
    """
    :param source: Has a current line
    :raises SingleInstructionInvalidArgumentException: If cannot parse a PathDdv
    """
    with token_stream_from_remaining_part_of_current_line_of_parse_source(source) as ts:
        return parse_path(ts, conf)


def parse_path_from_token_parser(conf: RelOptionArgumentConfiguration,
                                 token_parser: TokenParser,
                                 source_file_location: Optional[pathlib.Path] = None
                                 ) -> PathSdv:
    """
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    return parse_path(token_parser.token_stream, conf, source_file_location)


def parse_path(tokens: TokenStream,
               conf: RelOptionArgumentConfiguration,
               source_file_location: Optional[pathlib.Path] = None) -> PathSdv:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    return _parse_path(tokens, _Conf(source_file_location, conf))


class _Conf:
    def __init__(self,
                 source_file_location: Optional[pathlib.Path],
                 rel_opt_conf: RelOptionArgumentConfiguration
                 ):
        self.source_file_location = source_file_location
        self.rel_opt_conf = rel_opt_conf


def _parse_path(tokens: TokenStream,
                conf: _Conf) -> PathSdv:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    try:
        if conf.rel_opt_conf.path_suffix_is_required:
            return _parse_with_required_suffix(tokens, conf)
        else:
            return _parse_with_optional_suffix(tokens, conf)
    except TokenSyntaxError as ex:
        raise SingleInstructionInvalidArgumentException(
            std_error_message_text_for_token_syntax_error_from_exception(ex))


def _parse_with_required_suffix(tokens: TokenStream,
                                conf: _Conf) -> PathSdv:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    if tokens.is_null:
        _raise_missing_arguments_exception(conf)
    return _parse_with_non_empty_token_stream(tokens, conf)


def _parse_with_optional_suffix(tokens: TokenStream,
                                conf: _Conf) -> PathSdv:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """

    if tokens.is_null or tokens.remaining_part_of_current_line_is_empty:
        return _result_from_no_arguments(conf.rel_opt_conf)
    return _parse_with_non_empty_token_stream(tokens, conf)


def _parse_with_non_empty_token_stream(tokens: TokenStream,
                                       conf: _Conf) -> PathSdv:
    initial_argument_string = tokens.remaining_part_of_current_line
    relativity_info = parse_explicit_relativity_info(conf.rel_opt_conf.options,
                                                     conf.source_file_location,
                                                     tokens)

    if not conf.rel_opt_conf.path_suffix_is_required and tokens.remaining_part_of_current_line_is_empty:
        if relativity_info is None:
            return _result_from_no_arguments(conf.rel_opt_conf)
        else:
            path_part_sdv2_path_sdv = _path_constructor(relativity_info)
            return path_part_sdv2_path_sdv(path_part_sdvs.empty())

    if tokens.look_ahead_state is LookAheadState.NULL:
        raise SingleInstructionInvalidArgumentException(
            'Missing {} argument: {}'.format(conf.rel_opt_conf.argument_syntax_name,
                                             initial_argument_string))
    elif tokens.look_ahead_state is LookAheadState.SYNTAX_ERROR:
        SingleInstructionInvalidArgumentException(
            std_error_message_text_for_token_syntax_error(tokens.head_syntax_error_description))

    token = tokens.consume()
    if token.type is TokenType.PLAIN:
        ensure_is_not_option_argument(token.string)
    if relativity_info is None:
        return _without_explicit_relativity(token, conf.rel_opt_conf)
    else:
        path_part_2_path_sdv = _path_constructor(relativity_info)
        return _with_explicit_relativity(token, path_part_2_path_sdv)


def _without_explicit_relativity(path_argument: Token, conf: RelOptionArgumentConfiguration) -> PathSdv:
    string_fragments = parse_fragments_from_token(path_argument)
    if _string_fragments_is_constant(string_fragments):
        return _just_string_argument(path_argument.string, conf)
    else:
        return _just_argument_with_symbol_references(string_fragments, conf)


def _with_explicit_relativity(path_argument: Token,
                              path_part_2_path_sdv: Callable[[PathPartSdv], PathSdv]) -> PathSdv:
    string_sdv = _parse_string_sdv(path_argument)
    if string_sdv.is_string_constant:
        path_argument_str = string_sdv.string_constant
        path_argument_path = pathlib.PurePath(path_argument_str)
        if path_argument_path.is_absolute():
            return path_sdvs.constant(paths.absolute_file_name(path_argument_str))
        path_suffix = path_part_sdvs.from_constant_str(path_argument_str)
        return path_part_2_path_sdv(path_suffix)
    else:
        path_suffix = path_part_sdvs.from_string(string_sdv)
        return path_part_2_path_sdv(path_suffix)


def _just_string_argument(argument: str,
                          conf: RelOptionArgumentConfiguration) -> PathSdv:
    argument_path = pathlib.PurePath(argument)
    if argument_path.is_absolute():
        #  TODO Should we check if absolute paths are allowed according to RelOptionArgumentConfiguration??
        return path_sdvs.constant(paths.absolute_file_name(argument))
    path_suffix = paths.constant_path_part(argument)
    return path_sdvs.constant(paths.of_rel_option(conf.options.default_option,
                                                  path_suffix))


def _just_argument_with_symbol_references(string_fragments: list,
                                          conf: RelOptionArgumentConfiguration) -> PathSdv:
    if _first_fragment_is_symbol_that_can_act_as_path(string_fragments):
        path_or_str_sym_ref, path_suffix = _extract_parts_that_can_act_as_path_and_suffix(string_fragments,
                                                                                          conf)
        return _SdvThatIsIdenticalToReferencedPathOrWithStringValueAsSuffix(
            path_or_str_sym_ref,
            path_suffix,
            conf.options.default_option)
    else:
        #  TODO Check if fragments represent an absolute path
        path_suffix = _path_suffix_sdv_from_fragments(string_fragments)
        return _PathSdvOfRelativityOptionAndSuffixSdv(conf.options.default_option,
                                                      path_suffix)


def _result_from_no_arguments(conf: RelOptionArgumentConfiguration) -> PathSdv:
    return path_sdvs.constant(paths.of_rel_option(conf.options.default_option,
                                                  paths.empty_path_part()))


def _raise_missing_arguments_exception(conf: _Conf):
    msg = 'Missing %s argument' % conf.rel_opt_conf.argument_syntax_name
    raise SingleInstructionInvalidArgumentException(msg)


def _path_constructor(relativity_info: Union[RelOptionType, SymbolReference, pathlib.Path]
                      ) -> Callable[[PathPartSdv], PathSdv]:
    if isinstance(relativity_info, RelOptionType):
        return lambda path_suffix_sdv: _PathSdvOfRelativityOptionAndSuffixSdv(relativity_info,
                                                                              path_suffix_sdv)
    elif isinstance(relativity_info, SymbolReference):
        return functools.partial(path_sdvs.rel_symbol, relativity_info)
    elif isinstance(relativity_info, pathlib.Path):
        return lambda path_suffix_sdv: _PathSdvOfAbsPathAndSuffixSdv(relativity_info,
                                                                     path_suffix_sdv)

    else:
        raise TypeError("You promised you shouldn't give me a  " + str(relativity_info))


def _extract_parts_that_can_act_as_path_and_suffix(string_fragments: list,
                                                   conf: RelOptionArgumentConfiguration
                                                   ) -> (SymbolReference, PathPartSdv):
    path_or_string_symbol = SymbolReference(
        string_fragments[0].value,
        path_or_string_reference_restrictions(conf.options.accepted_relativity_variants),
    )
    path_part_sdv = _path_suffix_sdv_from_fragments(string_fragments[1:])
    return path_or_string_symbol, path_part_sdv


def path_or_string_reference_restrictions(
        accepted_relativity_variants: PathRelativityVariants) -> DataTypeReferenceRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            DataValueType.PATH,
            path_relativity_restriction(accepted_relativity_variants)),
        OrRestrictionPart(
            DataValueType.STRING,
            PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
    ],
        type_must_be_either_path_or_string__err_msg_generator
    )


def path_relativity_restriction(accepted_relativity_variants: PathRelativityVariants):
    return ReferenceRestrictionsOnDirectAndIndirect(
        PathRelativityRestriction(accepted_relativity_variants))


class _PathSdvOfRelativityOptionAndSuffixSdv(PathSdv):
    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix_sdv: PathPartSdv):
        self.relativity = relativity
        self.path_suffix_sdv = path_suffix_sdv

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        return paths.of_rel_option(self.relativity,
                                   self.path_suffix_sdv.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.path_suffix_sdv.references


class _PathSdvOfAbsPathAndSuffixSdv(PathSdv):
    def __init__(self,
                 abs_path_root: pathlib.Path,
                 path_suffix_sdv: PathPartSdv):
        self.abs_path_root = abs_path_root
        self.path_suffix_sdv = path_suffix_sdv
        if not self.abs_path_root.is_absolute():
            raise ValueError('abs_path_root is not absolute: ' + str(abs_path_root))

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        return paths.rel_abs_path(self.abs_path_root, self.path_suffix_sdv.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.path_suffix_sdv.references


def _parse_string_sdv(token: Token) -> StringSdv:
    return parse_string_sdv_from_token(token, PATH_COMPONENT_STRING_REFERENCES_RESTRICTION)


def _string_fragments_is_constant(fragments: list) -> bool:
    return len(fragments) == 1 and fragments[0].is_constant


def _first_fragment_is_symbol_that_can_act_as_path(fragments: list) -> bool:
    if fragments[0].is_constant:
        return False
    if len(fragments) == 1:
        return True
    fragment2 = fragments[1]
    return fragment2.is_constant and fragment2.value.startswith('/')


def _path_suffix_sdv_from_fragments(fragments: list) -> PathPartSdv:
    if not fragments:
        return path_part_sdvs.empty()
    string_sdv = string_sdv_from_fragments(fragments, PATH_COMPONENT_STRING_REFERENCES_RESTRICTION)
    return path_part_sdvs.from_string(string_sdv)


PATH_COMPONENT_STRING_REFERENCES_RESTRICTION = string_made_up_by_just_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'Every symbol used as a path component of a {path_type} '
            'must be defined as a {string_type}.',
            {
                'path_type': help_texts.DATA_TYPE_INFO_DICT[DataValueType.PATH].identifier,
                'string_type': help_texts.DATA_TYPE_INFO_DICT[DataValueType.STRING].identifier,
            },
        )
    )
)


def type_must_be_either_path_or_string__err_msg_generator(name_of_failing_symbol: str,
                                                          container_of_illegal_symbol: SymbolContainer) -> TextRenderer:
    value_restriction_failure = invalid_type_msg([ValueType.PATH, ValueType.STRING],
                                                 name_of_failing_symbol,
                                                 container_of_illegal_symbol)
    return ErrorMessageForDirectReference(value_restriction_failure)
