from pathlib import Path
from typing import Callable

from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers import token_stream_parsing
from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.test_case_utils import glob_pattern
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv, FileMatcherModel
from exactly_lib.util.parse import token_matchers
from . import sdv, defs, properties


def parser(
        model_property__glob_pattern: PropertyGetter[FileMatcherModel, Path],
        model_property__regex: PropertyGetter[FileMatcherModel, str],
) -> ParserFromTokens[FileMatcherSdv]:
    def parse_matcher_of_regex(token_parser: TokenParser) -> FileMatcherSdv:
        return sdv.reg_ex_sdv(model_property__regex,
                              _parse_regex(token_parser))

    def parse_matcher_of_glob_pattern(token_parser: TokenParser) -> FileMatcherSdv:
        return sdv.glob_pattern_sdv(model_property__glob_pattern,
                                    glob_pattern.parse(token_parser))

    return _parser(
        parse_matcher_of_regex,
        parse_matcher_of_glob_pattern,
    )


def parser_for_name_part(
        matcher_name: str,
        get_name_part_from_name: Callable[[str], str],
) -> ParserFromTokens[FileMatcherSdv]:
    property_getter = properties.NamePartAsStrPropertyGetter(matcher_name, get_name_part_from_name)

    def parse_matcher_of_regex(token_parser: TokenParser) -> FileMatcherSdv:
        return sdv.reg_ex_sdv(property_getter,
                              _parse_regex(token_parser))

    def parse_matcher_of_glob_pattern(token_parser: TokenParser) -> FileMatcherSdv:
        return sdv.glob_pattern_sdv__str(property_getter,
                                         glob_pattern.parse(token_parser))

    return _parser(
        parse_matcher_of_regex,
        parse_matcher_of_glob_pattern,
    )


def _parser(parse_matcher_of_regex: Callable[[TokenParser], FileMatcherSdv],
            parse_matcher_of_glob_pattern: Callable[[TokenParser], FileMatcherSdv],
            ) -> ParserFromTokens[FileMatcherSdv]:
    return token_stream_parsing.ParserOfMandatoryChoiceWithDefault(
        _SYNTAX_ELEM_STR,
        [
            token_stream_parsing.TokenSyntaxSetup(
                token_matchers.is_unquoted_and_equals(defs.REG_EX_OPERATOR.name),
                parse_matcher_of_regex,
            ),
        ],
        parse_matcher_of_glob_pattern,
    )


def _parse_regex(token_parser: TokenParser) -> RegexSdv:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=True)
    return regex_sdv


_SYNTAX_ELEM_STR = cl_syntax.cl_syntax_for_args((defs.GLOB_OR_REGEX__ARG_USAGE,))
