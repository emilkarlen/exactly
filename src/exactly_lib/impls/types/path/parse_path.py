import functools
import pathlib
from typing import Sequence, Optional, Callable, Union

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.impls.types.path.parse_relativity import parse_explicit_relativity_info
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.impls.types.string_.parse_string import parse_string_sdv_from_token, \
    parse_fragments_from_token, string_sdv_from_fragments
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import ensure_is_not_option_argument, \
    std_error_message_text_for_token_syntax_error_from_exception, std_error_message_text_for_token_syntax_error
from exactly_lib.section_document.element_parsers.token_stream import TokenStream, TokenSyntaxError, \
    LookAheadState
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.err_msg.error_messages import invalid_type_msg
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case import reserved_words, reserved_tokens
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import OrReferenceRestrictions, \
    OrRestrictionPart, ReferenceRestrictionsOnDirectAndIndirect, is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv, PathPartSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.parse.token import TokenType, Token, TokenMatcher
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


class PathParser:
    def __init__(self, conf: RelOptionArgumentConfiguration):
        self._conf = conf

    def parse(self,
              source: ParseSource,
              source_file_location: Optional[pathlib.Path] = None,
              ):
        with token_stream_parser.from_parse_source(source) as token_parser:
            return self.parse_from_token_parser(token_parser, source_file_location)

    def parse_from_token_parser(self,
                                parser: TokenParser,
                                source_file_location: Optional[pathlib.Path] = None,
                                ) -> PathSdv:
        return parse_path(parser.token_stream, self._conf, source_file_location)


def parse_path(tokens: TokenStream,
               conf: RelOptionArgumentConfiguration,
               source_file_location: Optional[pathlib.Path] = None) -> PathSdv:
    """
    :param tokens: Argument list
    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    conf = _Conf(source_file_location, conf)
    parser = _Parser(conf)
    if _token_stream_has_head(tokens, reserved_tokens.IS_PAREN__BEGIN):
        tokens.consume()
        ret_val = parser._parse_path__wo_parens(tokens)
        if _token_stream_has_head(tokens, reserved_tokens.IS_PAREN__END):
            tokens.consume()
            return ret_val
        else:
            raise SingleInstructionInvalidArgumentException(
                'Missing "{}" (unquoted)'.format(reserved_words.PAREN_END)
            )
    else:
        return parser._parse_path__wo_parens(tokens)


def _token_stream_has_head(token_stream: TokenStream, condition: TokenMatcher) -> bool:
    return (
            token_stream.look_ahead_state is LookAheadState.HAS_TOKEN
            and
            condition.matches(token_stream.head)
    )


class _Conf:
    def __init__(self,
                 source_file_location: Optional[pathlib.Path],
                 rel_opt_conf: RelOptionArgumentConfiguration
                 ):
        self.source_file_location = source_file_location
        self.rel_opt_conf = rel_opt_conf


class _Parser:
    def __init__(self, conf: _Conf):
        self.conf = conf

    def _parse_path__wo_parens(self, tokens: TokenStream) -> PathSdv:
        """
        :param tokens: Argument list
        :raises SingleInstructionInvalidArgumentException: Invalid arguments
        """

        try:
            if self.conf.rel_opt_conf.path_suffix_is_required:
                return self._with_required_suffix(tokens)
            else:
                return self._with_optional_suffix(tokens)
        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _with_required_suffix(self, tokens: TokenStream) -> PathSdv:
        """
        :param tokens: Argument list
        :raises SingleInstructionInvalidArgumentException: Invalid arguments
        """

        if tokens.look_ahead_state is LookAheadState.SYNTAX_ERROR:
            raise TokenSyntaxError(tokens.head_syntax_error_description)
        if tokens.is_null:
            self._raise_missing_arguments_exception()
        return self._with_non_empty_token_stream(tokens)

    def _with_optional_suffix(self, tokens: TokenStream) -> PathSdv:
        """
        :param tokens: Argument list
        :raises SingleInstructionInvalidArgumentException: Invalid arguments
        """

        if tokens.look_ahead_state is LookAheadState.SYNTAX_ERROR:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error(tokens.head_syntax_error_description))
        if tokens.is_null or tokens.remaining_part_of_current_line_is_empty:
            return self._result_from_no_arguments()
        return self._with_non_empty_token_stream(tokens)

    def _with_non_empty_token_stream(self, tokens: TokenStream) -> PathSdv:
        initial_argument_string = tokens.remaining_part_of_current_line
        relativity_info = parse_explicit_relativity_info(self.conf.rel_opt_conf.options,
                                                         self.conf.source_file_location,
                                                         tokens)

        if not self.conf.rel_opt_conf.path_suffix_is_required and tokens.remaining_part_of_current_line_is_empty:
            if relativity_info is None:
                return self._result_from_no_arguments()
            else:
                path_part_sdv2_path_sdv = self._path_constructor(relativity_info)
                return path_part_sdv2_path_sdv(path_part_sdvs.empty())

        if tokens.look_ahead_state is LookAheadState.SYNTAX_ERROR:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error(tokens.head_syntax_error_description))
        elif tokens.look_ahead_state is LookAheadState.NULL:
            raise SingleInstructionInvalidArgumentException(
                'Missing {}: {}'.format(self.conf.rel_opt_conf.argument_syntax_name,
                                        initial_argument_string))

        head_token = tokens.head

        if reserved_tokens.IS_RESERVED_WORD.matches(head_token):
            raise SingleInstructionInvalidArgumentException(
                'Illegal file name: {}'.format(head_token.string))
        elif head_token.type is TokenType.PLAIN:
            ensure_is_not_option_argument(head_token.source_string)

        tokens.consume()
        if relativity_info is None:
            return self._without_explicit_relativity(head_token)
        else:
            path_part_2_path_sdv = self._path_constructor(relativity_info)
            return self._with_explicit_relativity(head_token, path_part_2_path_sdv)

    def _without_explicit_relativity(self, path_argument: Token) -> PathSdv:
        string_fragments = parse_fragments_from_token(path_argument)
        if _string_fragments_is_constant(string_fragments):
            return self._just_string_argument(path_argument.string)
        else:
            return self._just_argument_with_symbol_references(string_fragments)

    def _with_explicit_relativity(self, path_argument: Token,
                                  path_part_2_path_sdv: Callable[[PathPartSdv], PathSdv]) -> PathSdv:
        string_sdv = _parse_string_sdv(path_argument)
        if string_sdv.is_string_constant:
            path_argument_str = string_sdv.string_constant
            path_argument_path = pathlib.PurePath(path_argument_str)
            if path_argument_path.is_absolute():
                return path_sdvs.constant(path_ddvs.absolute_file_name(path_argument_str))
            path_suffix = path_part_sdvs.from_constant_str(path_argument_str)
            return path_part_2_path_sdv(path_suffix)
        else:
            path_suffix = path_part_sdvs.from_string(string_sdv)
            return path_part_2_path_sdv(path_suffix)

    def _just_string_argument(self, argument: str,
                              ) -> PathSdv:
        argument_path = pathlib.PurePath(argument)
        if argument_path.is_absolute():
            #  TODO Should we check if absolute paths are allowed according to RelOptionArgumentConfiguration??
            return path_sdvs.constant(path_ddvs.absolute_file_name(argument))
        path_suffix = path_ddvs.constant_path_part(argument)
        return path_sdvs.constant(path_ddvs.of_rel_option(self.conf.rel_opt_conf.options.default_option,
                                                          path_suffix))

    def _just_argument_with_symbol_references(self, string_fragments: list,
                                              ) -> PathSdv:
        if _first_fragment_is_symbol_that_can_act_as_path(string_fragments):
            path_or_str_sym_ref, path_suffix = self._extract_parts_that_can_act_as_path_and_suffix(string_fragments)
            return path_sdvs.reference(
                path_or_str_sym_ref,
                path_suffix,
                self.conf.rel_opt_conf.options.default_option)
        else:
            #  TODO Check if fragments represent an absolute path
            path_suffix = _path_suffix_sdv_from_fragments(string_fragments)
            return _PathSdvOfRelativityOptionAndSuffixSdv(self.conf.rel_opt_conf.options.default_option,
                                                          path_suffix)

    def _result_from_no_arguments(self, ) -> PathSdv:
        return path_sdvs.constant(path_ddvs.of_rel_option(self.conf.rel_opt_conf.options.default_option,
                                                          path_ddvs.empty_path_part()))

    def _raise_missing_arguments_exception(self):
        msg = 'Missing ' + self.conf.rel_opt_conf.argument_syntax_name
        raise SingleInstructionInvalidArgumentException(msg)

    @staticmethod
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

    def _extract_parts_that_can_act_as_path_and_suffix(self, string_fragments: list,
                                                       ) -> (SymbolReference, PathPartSdv):
        path_or_string_symbol = SymbolReference(
            string_fragments[0].value,
            path_or_string_reference_restrictions(self.conf.rel_opt_conf.options.accepted_relativity_variants),
        )
        path_part_sdv = _path_suffix_sdv_from_fragments(string_fragments[1:])
        return path_or_string_symbol, path_part_sdv


def path_or_string_reference_restrictions(
        accepted_relativity_variants: PathRelativityVariants) -> WithStrRenderingTypeRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            WithStrRenderingType.PATH,
            path_relativity_restriction(accepted_relativity_variants)),
        OrRestrictionPart(
            WithStrRenderingType.STRING,
            PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
    ],
        type_must_be_either_path_or_string__err_msg_generator
    )


def path_relativity_restriction(accepted_relativity_variants: PathRelativityVariants):
    return ReferenceRestrictionsOnDirectAndIndirect(
        PathAndRelativityRestriction(accepted_relativity_variants))


class _PathSdvOfRelativityOptionAndSuffixSdv(PathSdv):
    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix_sdv: PathPartSdv):
        self.relativity = relativity
        self.path_suffix_sdv = path_suffix_sdv

    def resolve(self, symbols: SymbolTable) -> PathDdv:
        return path_ddvs.of_rel_option(self.relativity,
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
        return path_ddvs.rel_abs_path(self.abs_path_root, self.path_suffix_sdv.resolve(symbols))

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


PATH_COMPONENT_STRING_REFERENCES_RESTRICTION = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'Every symbol used as a path component of a {path_type} '
            'must be defined as a {string_type}.',
            {
                'path_type': help_texts.TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.PATH].identifier,
                'string_type': help_texts.TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.STRING].identifier,
            },
        )
    )
)


def type_must_be_either_path_or_string__err_msg_generator(name_of_failing_symbol: str,
                                                          container_of_illegal_symbol: SymbolContainer) -> TextRenderer:
    return invalid_type_msg([ValueType.PATH, ValueType.STRING],
                            name_of_failing_symbol,
                            container_of_illegal_symbol)
